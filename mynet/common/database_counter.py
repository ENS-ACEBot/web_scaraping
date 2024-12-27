import json
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python database_counter.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    try:
        with open(json_file_path, 'r') as file:
            news_list = json.load(file)
            print(f"Number of news items: {len(news_list)}")
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")

if __name__ == "__main__":
    main()