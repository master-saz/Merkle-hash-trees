# This is a sample Python script.
import os
import hashlib


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def create_headers(name):
    os.system("echo -n '\x35\x35\x35\x35\x35\x35' > docs/doc.pre")  # Creates the header for a document
    os.system("echo -n '\xe8\xe8\xe8\xe8\xe8\xe8' > nodes/node.pre")  # Creates the header for a node


def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


def merkle_tree(data_list):
    if len(data_list) == 1:
        return data_list

    new_data_list = []

    for i in range(0, len(data_list) - 1, 2):
        new_data_list.append(hash_data(data_list[i] + data_list[i + 1]))

    if len(data_list) % 2 == 1:
        new_data_list.append(hash_data(data_list[-1] + data_list[-1]))

    return merkle_tree(new_data_list)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_headers('PyCharm')
    """data_list = ["data1", "data2", "data3", "data4"]
    merkle_root = merkle_tree(list(map(hash_data, data_list)))[0]"""