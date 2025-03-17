import json
from new_class import News

def combine_json_files(file1, file2, output_file):
    # Read and parse both JSON files
    with open(file1, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)
    with open(file2, 'r', encoding='utf-8') as f2:
        data2 = json.load(f2)

    # Convert to News objects
    news_list1 = [News.from_dict(item) for item in data1]
    news_list2 = [News.from_dict(item) for item in data2]

    # Count original lengths
    length1, length2 = len(news_list1), len(news_list2)

    # Combine and track duplicates by news_url
    combined_dict = {}
    duplicate_dict = {}
    duplicate_count = 0
    for n in news_list1:
        if n.news_url in combined_dict:
            duplicate_count += 1
            duplicate_dict[n.news_url] = n
        else:
            combined_dict[n.news_url] = n
    print(f"duplicate_count 1st: {duplicate_count}")
    print(f"duplicated_dict 1st: {len(duplicate_dict)}")
    print(f"combined_dict 1st: {len(combined_dict)}")
    for n in news_list2:
        if n.news_url in combined_dict:
            duplicate_count += 1
            duplicate_dict = {}
        else:
            combined_dict[n.news_url] = n

    # Create combined list and sort
    combined_list = list(combined_dict.values())
    combined_list.sort()  # Depends on News.__lt__ by date_time

    # Calculate counts
    same_news_count = duplicate_count
    different_news_count = (length1 + length2) - same_news_count
    merged_count = len(combined_list)

    # Print required info
    print(f"Same news count: {same_news_count}")
    print(f"Different news count: {different_news_count}")
    print(f"File1 news count: {length1}, File2 news count: {length2}")
    print(f"New merged news count: {merged_count}")

    # Write new combined list to output JSON
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump([n.to_dict() for n in combined_list], out, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    file1 = "mynet_news_borsa copy.json"
    file2 = "mynet_news_ekonomi copy.json"
    output_file = "mynet_news_combined.json"
    combine_json_files(file1, file2, output_file)