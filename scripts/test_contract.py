import json
from pathlib import Path

from web3 import Web3
from web3.exceptions import ContractLogicError, Web3RPCError

RPC_URL = "http://127.0.0.1:7545"

SCRIPT_FOLDER = Path(__file__).resolve().parent


def check(condition, description):
    if not condition:
        raise AssertionError("FAIL: " + description)

    print("PASS:", description)


def expect_revert(function, sender, expected_message):
   
    try:
        function.call({"from": sender})
    except (ContractLogicError, Web3RPCError, ValueError) as error:
        if expected_message not in str(error):
            raise AssertionError(
                "The call failed for an unexpected reason: " + str(error)
            ) from error
        return

    raise AssertionError(
        "The contract accepted an action that should have been rejected."
    )


def main():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not web3.is_connected():
        print("Could not connect to Ganache.")
        print("Open Ganache and check RPC_URL.")
        raise SystemExit(1)

    accounts = web3.eth.accounts

    if len(accounts) < 3:
        print("At least three Ganache test accounts are required.")
        raise SystemExit(1)

    producer = accounts[0]
    distributor = accounts[1]
    retailer = accounts[2]
    abi_path = SCRIPT_FOLDER / "contract_abi.json"

    with abi_path.open(encoding="utf-8-sig") as file:
        abi = json.load(file)

    bytecode_path = SCRIPT_FOLDER / "contract_bytecode.txt"
    bytecode = bytecode_path.read_text(
        encoding="utf-8-sig"
    ).strip()

    if not bytecode:
        raise ValueError("contract_bytecode.txt is empty.")

    if not bytecode.startswith("0x"):
        bytecode = "0x" + bytecode

    factory = web3.eth.contract(abi=abi, bytecode=bytecode)

    transaction_hash = factory.constructor().transact(
        {"from": producer}
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    check(receipt.status == 1, "Test contract deployed")

    contract = web3.eth.contract(
        address=receipt.contractAddress,
        abi=abi
    )

    print("Test contract address:", receipt.contractAddress)
    print()

    check(
        contract.functions.batchCount().call() == 0,
        "New contract starts with zero batches"
    )

    expect_revert(
        contract.functions.createBatch(
            "",
            "County Meath, Ireland"
        ),
        producer,
        "Name is required"
    )
    print("PASS: Empty product name rejected")

    expect_revert(
        contract.functions.createBatch("Organic Tomatoes", ""),
        producer,
        "Origin is required"
    )
    print("PASS: Empty origin rejected")

    transaction_hash = contract.functions.createBatch(
        "Organic Tomatoes",
        "County Meath, Ireland"
    ).transact({"from": producer})

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    check(receipt.status == 1, "Batch creation transaction succeeded")

    batch = contract.functions.getBatch(1).call()

    check(
        contract.functions.batchCount().call() == 1
        and batch[0] == "Organic Tomatoes"
        and batch[1] == "County Meath, Ireland"
        and batch[2] == producer,
        "Batch details and initial owner are correct"
    )

    check(
        contract.functions.getTransferCount(1).call() == 0,
        "New batch has no transfers"
    )

    expect_revert(
        contract.functions.transferBatch(1, retailer),
        distributor,
        "Only the current owner can transfer this batch"
    )
    print("PASS: Non-owner transfer rejected")

    expect_revert(
        contract.functions.transferBatch(
            1,
            "0x0000000000000000000000000000000000000000"
        ),
        producer,
        "Receiver cannot be the zero address"
    )
    print("PASS: Zero-address receiver rejected")

    expect_revert(
        contract.functions.transferBatch(1, producer),
        producer,
        "Cannot transfer to yourself"
    )
    print("PASS: Self-transfer rejected")

    transaction_hash = contract.functions.transferBatch(
        1,
        distributor
    ).transact({"from": producer})

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    check(receipt.status == 1, "First transfer transaction succeeded")

    batch = contract.functions.getBatch(1).call()
    first_transfer = contract.functions.getTransfer(1, 0).call()

    check(
        batch[2] == distributor
        and contract.functions.getTransferCount(1).call() == 1
        and first_transfer[0] == producer
        and first_transfer[1] == distributor
        and first_transfer[2] > 0,
        "First transfer changed ownership and saved history"
    )

    expect_revert(
        contract.functions.transferBatch(1, retailer),
        producer,
        "Only the current owner can transfer this batch"
    )
    print("PASS: Previous owner can no longer transfer the batch")

    transaction_hash = contract.functions.transferBatch(
        1,
        retailer
    ).transact({"from": distributor})

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    check(receipt.status == 1, "Second transfer transaction succeeded")

    batch = contract.functions.getBatch(1).call()
    second_transfer = contract.functions.getTransfer(1, 1).call()

    check(
        batch[2] == retailer
        and contract.functions.getTransferCount(1).call() == 2
        and second_transfer[0] == distributor
        and second_transfer[1] == retailer
        and second_transfer[2] > 0,
        "Second transfer changed ownership and saved history"
    )

    check(
        contract.functions.getTransfer(1, 0).call()
        == first_transfer,
        "First history record is unchanged"
    )

    expect_revert(
        contract.functions.getBatch(99),
        producer,
        "Batch does not exist"
    )
    print("PASS: Nonexistent batch rejected")

    expect_revert(
        contract.functions.getTransfer(1, 2),
        producer,
        "Transfer does not exist"
    )
    print("PASS: Invalid transfer index rejected")

    print("\nAll automated checks passed!")


if __name__ == "__main__":
    main()