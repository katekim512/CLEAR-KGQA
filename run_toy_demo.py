import fire

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


def main(
    qid="WebQTest-516.P0",
    model_name="gpt-4o-2024-08-06",
    note="toy-kg-demo",
):
    model_dir = model_name.split("/")[-1]
    save_dir = f"save/{note}/webqsp/{model_dir}-one-question"
    example = find_example(qid)
    dummy_user = DummyUser(
        qid=example["id"],
        sparql=example["sparql"],
        entity_desc=example["entity_desc"],
        model_name="gpt-4o-2024-08-06",
    )
    kg_agent = KGAgent(
        q=example["question"],
        qid=example["id"],
        dataset=example["dataset"],
        model_name=model_name,
    )
    kg_agent.run(call_back=dummy_user, plugin=False)
    result = kg_agent.to_dict()
    result["answers"] = example["answers"]
    result["sparql"] = example["sparql"]
    result["infer_chain"] = example["infer_chain"]

    save_to_json(dummy_user.to_dict(), f"{save_dir}/{qid}-dummy_user.json")
    save_to_pkl(dummy_user, f"{save_dir}/{qid}-dummy_user.pkl")
    save_to_json(result, f"{save_dir}/{qid}-kg_agent.json")
    save_to_pkl(kg_agent, f"{save_dir}/{qid}-kg_agent.pkl")

    print(f"Prediction: {result['prediction']}")
    print(f"Gold answers: {result['answers']}")
    print(f"Finished {qid}. Results saved to {save_dir}")


if __name__ == "__main__":
    fire.Fire(main)
