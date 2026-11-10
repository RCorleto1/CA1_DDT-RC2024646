from web3 import Web3

RPC_URL = "http://127.0.0.1:7545"


def main():
    
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not web3.is_connected():
        print("Could not connect to Ganache.")
        print("Open Ganache and check the RPC server address.")
        raise SystemExit(1)

    print("Connected to Ganache!")
    print("Chain ID:", web3.eth.chain_id)
    print("Latest block:", web3.eth.block_number)

    accounts = web3.eth.accounts

    print("Number of test accounts:", len(accounts))

    for number, account in enumerate(accounts, start=1):
        balance = web3.eth.get_balance(account)
        balance_in_eth = web3.from_wei(balance, "ether")

        print()
        print("Account", number)
        print("Address:", account)
        print("Balance:", balance_in_eth, "ETH")


if __name__ == "__main__":
    main()