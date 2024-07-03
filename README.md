# Huawei Developer Conference 2024 (São Paulo, Brazil) Terraform Activity

This project was developed for the Huawei Developer Conference 2024 held in São Paulo, Brazil. It checks the correctness of resources created using Terraform, processes the results, and generates a sorted CSV file based on the scores and creation times of the resources.

## Project Structure

The project consists of three main files:

- `check_terraform.py`: Contains the logic to verify if the resources created by Terraform match the expected configurations.
- `main.py`: Processes user directories, calculates scores, and writes the results to a CSV file. It also sorts the entries based on scores and creation times.
- `merge_sort.py`: Implements the merge sort algorithm to sort the CSV entries.

## Files

### `check_terraform.py`

This script verifies the correctness of the resources created from the `terraform.tfstate` file. It checks various attributes of resources such as VPC, Subnet, Security Group, ECS, EIP, RDS, and GaussDB instances.

### `main.py`

This script processes the directories, executes the checks using `check_terraform.py`, and writes the scores and creation times to a CSV file. It then sorts the CSV entries based on scores and creation times using the merge sort algorithm from `merge_sort.py`.

### `merge_sort.py`

This script implements the merge sort algorithm to sort the entries in the CSV file. It ensures that the entries are sorted by scores in descending order, and if the scores are the same, it sorts by the oldest creation time.

## Usage

To run this project, follow these steps:

1. Ensure you have Python installed on your machine.
2. Place the `terraform.tfstate` files in the respective user directories inside a base directory.
3. Execute the following command:

```sh
python main.py -d <base_directory> -o <output_csv>
```
