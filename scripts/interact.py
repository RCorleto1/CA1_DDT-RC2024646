import json
from pathlib import Path

from web3 import Web3

RPC_URL = "http://127.0.0.1:7545"

SCRIPT_FOLDER = Path(__file__).resolve().parent


def main():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not web3.is_connected():
        print("Could not connect to Ganache.")
        print("Check that Ganache is open and RPC_URL is correct.")
        raise SystemExit(1)

    accounts = web3.eth.accounts

    if len(accounts) < 2:
        print("At least two Ganache test accounts are required.")
        raise SystemExit(1)

    producer = accounts[0]
    retailer = accounts[1]

    abi_path = SCRIPT_FOLDER / "contract_abi.json"

    with abi_path.open(encoding="utf-8-sig") as file:
        abi = json.load(file)

    bytecode_path = SCRIPT_FOLDER / "contract_bytecode.txt"
    bytecode = bytecode_path.read_text(
        encoding="utf-8-sig"
    ).strip()

    if not bytecode:
        print("contract_bytecode.txt is empty.")
        raise SystemExit(1)

    if not bytecode.startswith("0x"):
        bytecode = "0x" + bytecode

    print("Connected to Ganache.")
    print("Producer:", producer)
    print("Retailer:", retailer)

    contract_factory = web3.eth.contract(
        abi=abi,
        bytecode=bytecode
    )

    print("\nDeploying the contract...")

    transaction_hash = contract_factory.constructor().transact(
        {"from": producer}
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    if receipt.status != 1:
        raise RuntimeError("Contract deployment failed.")

    contract_address = receipt.contractAddress

    print("Contract deployed at:", contract_address)

    contract = web3.eth.contract(
        address=contract_address,
        abi=abi
    )

    print("\nCreating a food batch...")

    transaction_hash = contract.functions.createBatch(
        "Organic Tomatoes",
        "County Meath, Ireland"
    ).transact({"from": producer})

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    if receipt.status != 1:
        raise RuntimeError("Batch creation failed.")

    batch_id = contract.functions.batchCount().call()

    print("Batch ID:", batch_id)

    batch = contract.functions.getBatch(batch_id).call()

    print("Name:", batch[0])
    print("Origin:", batch[1])
    print("Owner before transfer:", batch[2])

    print("\nTransferring the batch to the retailer...")

    transaction_hash = contract.functions.transferBatch(
        batch_id,
        retailer
    ).transact({"from": producer})

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    if receipt.status != 1:
        raise RuntimeError("Batch transfer failed.")

    batch = contract.functions.getBatch(batch_id).call()

    print("Owner after transfer:", batch[2])

    transfer_count = contract.functions.getTransferCount(
        batch_id
    ).call()

    print("\nNumber of transfers:", transfer_count)

    transfer = contract.functions.getTransfer(
        batch_id,
        0
    ).call()

    print("Sender:", transfer[0])
    print("Receiver:", transfer[1])
    print("Timestamp:", transfer[2])

    print("\nFood traceability demonstration completed!")


if __name__ == "__main__":
    main()