import fire

import agent.kg as kg_module
from agent import DummyUser, KGAgent
from common.common_utils import read_json, save_to_json, save_to_pkl


def find_example(qid):
    paths = [
        "dataset_processed-v2.0/webqsp/test-300/chain_len_1.json",
        "dataset_processed-v2.0/webqsp/test-300/chain_len_2.json",
    ]
    for path in paths:
        for item in read_json(path):
            if item["id"] == qid:
                item["dataset"] = "webqsp"
                return item
    raise ValueError(f"qid not found: {qid}")


class ScriptedToyUser:
    def __init__(self, qid):
        self.qid = qid
        self.messages = []

    def __call__(self, question):
        answer = (
            "I mean Malaysia, the federal constitutional monarchy located in "
            "Southeast Asia, not the fictional film entry."
        )
        print(f"ToyUser clarification question: {question}")
        print(f"ToyUser answer: {answer}")
        self.messages.append(
            {
                "clarification_question": question,
                "answer": answer,
            }
        )
        return answer

    def to_dict(self):
        return {
            "qid": self.qid,
            "messages": self.messages,
        }


def force_toy_ambiguity():
    kg_module.calculate_ambiguous_score_for_entity = lambda q, action_str: 1.0
    kg_module.calculate_ambiguous_score_for_intention = (
        lambda q, topic_entity, search_predicate_res: 0.0
    )


def main(
    qid="WebQTest-516.P0",
    model_name="gpt-4o-2024-08-06",
    note="toy-clarification-demo",
    use_real_ppl=False,
    user_mode="dummy",
):
    if not use_real_ppl:
        force_toy_ambiguity()

    model_dir = model_name.split("/")[-1]
    ppl_mode = "real-ppl" if use_real_ppl else "forced-ppl"
    save_dir = f"save/{note}/webqsp/{model_dir}-{ppl_mode}-one-question"
    example = find_example(qid)
    if user_mode == "dummy":
        toy_user = DummyUser(
            qid=example["id"],
            sparql=example["sparql"],
            entity_desc=example["entity_desc"],
            model_name=model_name,
        )
    elif user_mode == "scripted":
        toy_user = ScriptedToyUser(qid=example["id"])
    else:
        raise ValueError("user_mode must be one of: dummy, scripted")

    kg_agent = KGAgent(
        q=example["question"],
        qid=example["id"],
        dataset=example["dataset"],
        model_name=model_name,
        ambiguous_score_entity_threshold=0.6,
        ambiguous_score_intention_threshold=0.8,
    )
    kg_agent.prompt_text += """

Toy clarification demo rule:
If SearchNodes returns multiple descriptions for the same entity name and the observation contains an ambiguity hint, ask exactly one AskForClarification question before selecting the entity.
""".strip()

    kg_agent.run(call_back=toy_user, plugin=True)
    result = kg_agent.to_dict()
    result["answers"] = example["answers"]
    result["sparql"] = example["sparql"]
    result["infer_chain"] = example["infer_chain"]

    save_to_json(toy_user.to_dict(), f"{save_dir}/{qid}-{user_mode}_user.json")
    save_to_pkl(toy_user, f"{save_dir}/{qid}-{user_mode}_user.pkl")
    save_to_json(result, f"{save_dir}/{qid}-kg_agent.json")
    save_to_pkl(kg_agent, f"{save_dir}/{qid}-kg_agent.pkl")

    print(f"User mode: {user_mode}")
    print(f"User simulator: {toy_user.to_dict()}")
    print(f"Prediction: {result['prediction']}")
    print(f"Gold answers: {result['answers']}")
    print(f"Finished {qid}. Results saved to {save_dir}")


if __name__ == "__main__":
    fire.Fire(main)
