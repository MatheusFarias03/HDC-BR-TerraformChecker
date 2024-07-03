import os, csv, argparse, merge_sort
from check_terraform import execute

def write_csv_from_dirs(base_dir:str, output_csv:str) -> None:

    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "score", "time"]) # TODO: Mudar aqui

        # Iterate through each directory in the base directory.
        for user in os.listdir(base_dir):
            user_dir = os.path.join(base_dir, user)
            
            if os.path.isdir(user_dir):
                terraform_state_file = os.path.join(user_dir, "terraform.tfstate")
                
                if os.path.exists(terraform_state_file):
                    try:
                        score, creation_time = execute(terraform_state_file, user) # TODO: Mudar aqui
                        writer.writerow([user, score, creation_time]) # TODO: Mudar aqui

                    except Exception as e:
                        print(f"Error processing {terraform_state_file}: {e}")
                else:
                    print(f"terraform.tfstate file not found in {user_dir}")


def write_ordered_csv(output_csv:str, arr):
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        for element in arr:
            writer.writerow(element)


def order_csv_by_score_and_date(input_csv:str):

    users_arr = []

    with open(input_csv, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            users_arr.append(row)

    # Convert the score, that is a string, into integer.
    for i in range(1, len(users_arr)):
        users_arr[i][1] = int(users_arr[i][1])
    
    merge_sort.merge_sort(users_arr, 1, len(users_arr)-1)
    # merge_sort.merge_sort()

    time_score = 70
    for i in range(1, len(users_arr)):
        if time_score > 0:
            users_arr[i][1] += time_score
            time_score -= 7
    
    return users_arr
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Terraform state files.")
    parser.add_argument('-d', '--directory', type=str, required=True, help="The base directory containing user directories")
    parser.add_argument('-o', '--output', type=str, required=True, help="The output CSV file name")

    args = parser.parse_args()
    
    write_csv_from_dirs(args.directory, args.output)
    users_arr = order_csv_by_score_and_date(args.output)
    write_ordered_csv(args.output, users_arr)
