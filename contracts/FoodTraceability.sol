// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

contract FoodTraceability {

    struct FoodBatch {
        string name;
        string origin;
        address owner;
    }

    uint256 public batchCount;

    mapping(uint256 => FoodBatch) public batches;

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
}