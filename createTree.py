# This is a sample Python script.
import os
import hashlib
import sys


def create_headers(name):
    os.system("echo -n '\x35\x35\x35\x35\x35\x35' > docs/doc.pre")  # Creates the header for a document
    os.system("echo -n '\xe8\xe8\xe8\xe8\xe8\xe8' > nodes/node.pre")  # Creates the header for a node


def hash_file(file_path, prefix):
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.sha1(prefix + content).hexdigest()


def merkle_tree(n, prefix1, prefix2):
    tree = []
    for i in range(n):
        file_path = f'docs/doc{i}.dat'
        tree.append((0, i, hash_file(file_path, prefix1)))

    i = 0
    while len(tree) > 1:
        new_level = []
        for j in range(0, len(tree), 2):
            if j + 1 < len(tree):
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(tree[j][2]) + bytes.fromhex(tree[j + 1][2])).hexdigest()
                new_level.append((i + 1, j // 2, combined_hash))
            else:
                new_level.append((i + 1, j // 2, tree[j][2]))
        tree = new_level
        i += 1

    return tree[0]


def update_tree(new_doc, prefix1, prefix2):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split(':')
    n = int(header[4])
    depth = int(header[5])

    new_leaf = (0, n, hash_file(new_doc, prefix1))
    tree = [tuple(map(int, line.strip().split(':'))) for line in lines[1:]]
    tree.append(new_leaf)

    for i in range(depth - 1):
        parent = (i + 1, n // 2, hashlib.sha1(prefix2 + bytes.fromhex(tree[-2][2]) + bytes.fromhex(tree[-1][2])).hexdigest())
        tree.append(parent)
        n //= 2

    with open('tree.txt', 'w') as f:
        f.write(':'.join(header[:4] + [str(int(header[4]) + 1), header[5], tree[-1][2]]) + '\n')
        for node in tree:
            f.write(':'.join(map(str, node)) + '\n')


def generate_proof(doc, position):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    tree = [tuple(map(int, line.strip().split(':'))) for line in lines[1:]]
    proof = []

    i = 0
    j = position
    while i < len(tree) and tree[i][0] != 0:
        if j % 2 == 0:
            proof.append(tree[i + j + 1])
        else:
            proof.append(tree[i + j - 1])
        i += 2 ** tree[i][0]
        j //= 2

    return proof


def verify_proof(doc, proof):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split(':')
    prefix1 = bytes.fromhex(header[2])
    prefix2 = bytes.fromhex(header[3])
    root_hash = header[6]

    current_hash = hash_file(doc, prefix1)
    position = proof[0][1]

    for node in proof:
        if position % 2 == 0:
            combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(current_hash) + bytes.fromhex(node[2])).hexdigest()
        else:
            combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(node[2]) + bytes.fromhex(current_hash)).hexdigest()
        current_hash = combined_hash
        position //= 2

    return current_hash == root_hash


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #create_headers('PyCharm')
    #data_list = ["data1", "data2", "data3", "data4"]
    #merkle_root = merkle_tree(list(map(hash_data, data_list)))[0]
    prefix1 = bytes.fromhex('353535353535')
    prefix2 = bytes.fromhex('e8e8e8e8e8e8')
    merkle_root = merkle_tree(4, prefix1, prefix2)
    print(merkle_root)