import multiprocessing
import re

import requests

requestUrl = "https://ep.atomicals.xyz/proxy/blockchain.atomicals.get"
max_retry = 3


def split_range_into_chunks(start, end, chunk_size):
    chunks = []
    for i in range(start, end, chunk_size):
        chunk_start = i
        chunk_end = min(i + chunk_size, end)
        chunks.append((chunk_start, chunk_end))
    return chunks


def worker_function(start, end):
    result = []
    for num in range(start, end):
        find_file_name = ""
        body = {"params": [str(num)]}
        retry = 0
        while True:
            try:
                if retry >= max_retry:
                    break
                response = requests.post(requestUrl, json=body)
                if response.status_code == 200:
                    mint_data = response.json()['response']['result']['mint_data']['fields']
                    bit_work_c = mint_data['args']['bitworkc']
                    print(f"bit_work_c:{bit_work_c}~{mint_data['args']}")
                    if mint_data['args'] is None:
                        break
                    if mint_data['args']['bitworkc'] is None:
                        break
                    for key in mint_data:
                        if "atommap.svg" in key:
                            print(f"{bit_work_c}～{key}")
                            find_file_name = key
                    if len(find_file_name) == 0:
                        retry = retry + 1
                        continue
                    match = re.search(r'\b\d+\b', find_file_name[::-1])
                    if match:
                        last_number_reversed = match.group()[::-1]  # 反转回来以得到最后一个数字
                        bit_work_c = bit_work_c.replace("ab", "")
                        if last_number_reversed != bit_work_c:
                            print("miss match" + bit_work_c + ":" + last_number_reversed)
                            break
                        else:
                            print("push:" + last_number_reversed)
                            result.append(int(last_number_reversed))
                            break
                    else:
                        print(f"{find_file_name}未找到数字")
                        retry = retry + 1
                        continue
                else:
                    print(f"Request failed with status code {response.status_code}:{response.text}")
                    retry = retry + 1
            except Exception as e:
                retry = retry + 1
                print(e)
    return result


def handler(start, end, num_processes):
    chunk_size = (end - start) // num_processes
    chunks = split_range_into_chunks(start, end, chunk_size)
    with multiprocessing.Pool(num_processes) as pool:
        results = pool.starmap(worker_function, chunks)
    merged_array = []
    for arr in results:
        merged_array.extend(arr)
    unique_numbers = list(set(merged_array))
    merged_array = sorted(unique_numbers)
    for i in range(len(merged_array) - 1):
        if merged_array[i] + 1 != merged_array[i + 1]:
            print(f"在索引 {i} 和 {i + 1} 处的元素不满足条件: {merged_array[i]} ～ {merged_array[i + 1]}")
    with open('output.txt', 'a') as file:
        for item in merged_array:
            file.write(str(item) + "\n")


if __name__ == '__main__':
     # // 60526
    handler(55706, 60526, 16)
