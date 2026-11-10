// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

contract FoodTraceability {

    struct FoodBatch {
        string name;
        string origin;
        address owner;
    }

    struct TransferRecord {
        address sender;
        address receiver;
        uint256 timestamp;
    }

    uint256 public batchCount;

    mapping(uint256 => FoodBatch) public batches;

    mapping(uint256 => TransferRecord[]) private transferHistory;

    function createBatch(
        string memory _name,
        string memory _origin
    ) public {
        require(bytes(_name).length > 0, "Name is required");
        require(bytes(_origin).length > 0, "Origin is required");

        batchCount++;

        batches[batchCount] = FoodBatch({
            name: _name,
            origin: _origin,
            owner: msg.sender
        });
    }

    function getBatch(uint256 _batchId)
        public
        view
        returns (
            string memory name,
            string memory origin,
            address owner
        )
    {
        require(
            _batchId > 0 && _batchId <= batchCount,
            "Batch does not exist"
        );

        FoodBatch memory batch = batches[_batchId];

        return (
            batch.name,
            batch.origin,
            batch.owner
        );
    }
    
    function transferBatch(
        uint256 _batchId,
        address _newOwner
    ) public {
        require(
            _batchId > 0 && _batchId <= batchCount,
            "Batch does not exist"
        );

        require(
            batches[_batchId].owner == msg.sender,
            "Only the current owner can transfer this batch"
        );

        require(
            _newOwner != address(0),
            "Receiver cannot be the zero address"
        );

        require(
            _newOwner != msg.sender,
            "Cannot transfer to yourself"
        );

        transferHistory[_batchId].push(
            TransferRecord({
                sender: msg.sender,
                receiver: _newOwner,
                timestamp: block.timestamp
            })
        );

        batches[_batchId].owner = _newOwner;
    }

    function getTransferCount(uint256 _batchId)
        public
        view
        returns (uint256)
    {
        require(
            _batchId > 0 && _batchId <= batchCount,
            "Batch does not exist"
        );

        return transferHistory[_batchId].length;
    }

    function getTransfer(
        uint256 _batchId,
        uint256 _index
    )
        public
        view
        returns (
            address sender,
            address receiver,
            uint256 timestamp
        )
    {
        require(
            _batchId > 0 && _batchId <= batchCount,
            "Batch does not exist"
        );

        require(
            _index < transferHistory[_batchId].length,
            "Transfer does not exist"
        );

        TransferRecord memory record =
            transferHistory[_batchId][_index];

        return (
            record.sender,
            record.receiver,
            record.timestamp
        );
    }
}