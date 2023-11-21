# This is a sample Python script.
import os
import hashlib
import sys
import math


def create_headers(name):
    os.system("echo -n '\x35\x35\x35\x35\x35\x35' > docs/doc.pre")  # Creates the header for a document
    os.system("echo -n '\xe8\xe8\xe8\xe8\xe8\xe8' > nodes/node.pre")  # Creates the header for a node


def hash_file(file_path, prefix):
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.sha1(prefix + content).hexdigest()


def merkle_tree(n, prefix1, prefix2):
    open("temp.txt", 'w').close()
    tree = []
    for i in range(n):
        file_path = f'docs/doc{i}.dat'
        doc_hash = hash_file(file_path, prefix1)
        tree.append((0, i, doc_hash))
        with open(f'nodes/node{0}.{i}', 'w') as f:
            f.write(doc_hash)

        with open(f'temp.txt', 'a') as f:
            public_info = f"\n{0}:{i}:{doc_hash}"  # update tree.txt
            f.write(public_info)

    i = 0
    while len(tree) > 1:
        new_level = []
        for j in range(0, len(tree), 2):
            if j + 1 < len(tree):
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(tree[j][2]) + bytes.fromhex(tree[j + 1][2])).hexdigest()
                new_level.append((i + 1, j // 2, combined_hash))
                with open(f'nodes/node{i+1}.{j // 2}', 'w') as f:
                    f.write(combined_hash)

                with open(f'temp.txt', 'a') as f:
                    public_info = f"\n{i+1}:{j // 2}:{combined_hash}" #update tree.txt
                    f.write(public_info)
            else:
                new_level.append((i + 1, j // 2, tree[j][2]))
                with open(f'nodes/node{i+1}.{j // 2}', 'w') as f:
                    f.write(tree[j][2])

                with open(f'temp.txt', 'a') as f:
                    public_info = f"\n{i+1}:{j // 2}:{tree[j][2]}" #update tree.txt
                    f.write(public_info)
        tree = new_level
        i += 1

    f = open('temp.txt', 'r')
    temp = f.read()
    f.close()

    f = open('tree.txt', 'w')
    public_info = f"MerkleTree:sha1:{prefix1.hex()}:{prefix2.hex()}:{n}:{i}:{tree[0][-1]}"  # public info of the hash tree
    f.write(public_info)

    f.write(temp)
    f.close()

    return tree[0]


def update_tree(new_doc, prefix1, prefix2):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split(':')
    n = int(header[4])

    new_leaf = (f"{0}", f"{n}", hash_file(new_doc, prefix1))
    tree = [tuple(map(str, line.strip().split(':'))) for line in lines[1:]]
    tree.append(new_leaf)

    depth = math.ceil(math.log(n+1, 2))
    #print(tree)
    tmp_dict = dict((f"{x}{y}", h) for x, y , h in tree)

    for i in range(depth):
        # check if node is odd or even, to determine how you get the hash (previous one or next/empty one).

        if n % 2==0: #using the next one
            try:
                hash = tmp_dict[f"{i}{n+1}"]
                parent = (f"{i + 1}", f"{n // 2}",
                          hashlib.sha1(prefix2 + bytes.fromhex(tmp_dict[f"{i}{n}"]) + bytes.fromhex(hash)).hexdigest())
            except:
                parent = (f"{i + 1}", f"{n // 2}", hashlib.sha1(prefix2 + bytes.fromhex(tmp_dict[f"{i}{n}"])).hexdigest())
            tree.append(parent)
        else: # using the previous one
            try:
                hash = tmp_dict[f"{i}{n-1}"]
                parent = (f"{i + 1}", f"{n // 2}",
                          hashlib.sha1(prefix2 + bytes.fromhex(hash) + bytes.fromhex(tmp_dict[f"{i}{n}"])).hexdigest())

            except:
                parent = (f"{i + 1}", f"{n // 2}", hashlib.sha1(prefix2 + bytes.fromhex(tmp_dict[f"{i}{n}"])).hexdigest())

            for node in tree: # deal with duplicates
                if int(node[0])==i+1 and int(node[1]) == n//2:
                    tree.remove(node)
            tree.append(parent)
        tmp_dict[f"{i+1}{n // 2}"]=parent[2]
        with open(f'nodes/node{i + 1}.{n // 2}', 'w') as f:
            f.write(parent[2])
        n //= 2
    #print(tmp_dict)
    tree = sorted(tree, key=lambda element: (element[0], element[1]))

    with open('tree.txt', 'w') as f:
        f.write(':'.join(header[:4] + [str(int(header[4]) + 1), str(depth+1), tree[-1][2]]) + '\n')
        for node in tree:
            f.write(':'.join(map(str, node)) + '\n')


def generate_proof(doc, position):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split(':')
    depth = int(header[5])

    tree = [tuple(map(str, line.strip().split(':'))) for line in lines[1:]]
    tmp_dict = dict((f"{x}{y}", h) for x, y, h in tree)

    proof = []
    i = 0
    j = position

    while i < depth-1:
        if j % 2 == 0:
            #print(f"node{i} {j+1}")
            #proof.append(f"node{i}.{j+1}")
            try:
                hash= tmp_dict[f"{i}{j+1}"]
                proof.append((f"{i}", f"{j + 1}", hash))
            except:
                proof.append((f"{i}", f"{j + 1}", ""))

        else:
            #print(f"node{i} {j - 1}")
            #proof.append(f"node{i}.{j-1}")
            try:
                hash= tmp_dict[f"{i}{j-1}"]
                proof.append((f"{i}", f"{j - 1}", hash))
            except:
                proof.append((f"{i}", f"{j - 1}", ""))

        i += 1
        j //= 2

    #print(proof)
    return proof


def verify_proof(doc, proof):
    with open('tree.txt', 'r') as f:
        lines = f.readlines()

    header = lines[0].strip().split(':')
    prefix1 = bytes.fromhex(header[2])
    prefix2 = bytes.fromhex(header[3])
    root_hash = header[6]

    current_hash = hash_file(doc, prefix1)
    #print(position)
    for node in proof:
        if int(node[1]) % 2 == 0:  # using the next one
            if node[2] == "":
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(current_hash)).hexdigest()
            #print(f"current: {node[2]}")
            else:
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(node[2]) + bytes.fromhex(current_hash)).hexdigest()
        else:
            if node[2] == "":
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(current_hash)).hexdigest()
            #print(f"current: {node[2]}")
            else:
                combined_hash = hashlib.sha1(prefix2 + bytes.fromhex(current_hash) + bytes.fromhex(node[2])).hexdigest()
        current_hash = combined_hash
        #print(combined_hash)

    return current_hash == root_hash


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    prefix1 = bytes.fromhex('353535353535')
    prefix2 = bytes.fromhex('e8e8e8e8e8e8')
    merkle_root = merkle_tree(4, prefix1, prefix2)
    #print(merkle_root)
    print(f"Original Root: {merkle_root}")

    update_tree(f'docs/doc4.dat', prefix1, prefix2)
    proof = generate_proof("",4) #position being 0.x
    print(f"Proof: {proof}")
    print(f"Verifying proof: {verify_proof("docs/doc4.dat", proof)}")