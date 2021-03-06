import json
import math
import pprint
import random
import numpy as np
from collections import defaultdict

json_file = open("./partial/inverted_subreddits.json", 'r')
users_file = open("./partial/users.txt", 'r')
defaults_file = open("./partial/defaults.json", 'r')
outfile = open('data2.json', 'w')
subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

n_clusters_per_level = 40
kmeans_cycles = 2
users_threshold = 50

users = []
for line in users_file:
	users.append(line.split("\t")[0])


def kmeans (this_subs_dict):

	centers = []
	clusters = {}
	cycle = 0

	for i in range(n_clusters_per_level):
		centers.append(random.choice(this_subs_dict.keys()))

	while (cycle < kmeans_cycles):

		print "\n\n ***** CYCLE " + str(cycle) + " *****\n\n"	

		clusters = {}

		for center in centers:
			clusters[center] = []

		count = 0
		for sub in this_subs_dict:
			max_similarity = 0
			candidate = ""
			for center in centers:
				size_of_intersection = 0
				for user in this_subs_dict[sub]:
					if user in this_subs_dict[center]: size_of_intersection += 1
				similarity = size_of_intersection / math.sqrt(len(this_subs_dict[center])*len(this_subs_dict[sub]))
				if similarity >= max_similarity:
					max_similarity = similarity
					candidate = center
			clusters[candidate].append(sub)

			count+=1
			print count,

		pprint.pprint(clusters)

		"""
		centers = []
		for item in clusters:
			
			avg = defaultdict(float)
			num_of_users_not_zero = 0
			for sub in clusters[item]:
				for user in this_subs_dict[sub]:
					avg[user] += 1
			for user in avg:
				avg[user] = int(round(avg[user]/len(clusters[item])))
				if avg[user] != 0: num_of_users_not_zero += 1

			candidate = ""
			max_similarity = 0
			for sub in clusters[item]:
				size_of_intersection = 0
				for user in avg:
					if avg[user] != 0 and user in this_subs_dict[sub]:
						size_of_intersection += 1
				divisor = math.sqrt(num_of_users_not_zero * len(this_subs_dict[sub]))
				if divisor == 0:
					similarity = 0
				else:
					similarity = size_of_intersection / divisor
				if similarity >= max_similarity:
					max_similarity = similarity
					candidate = sub
			centers.append(candidate)
		"""
		centers = []

		for item in clusters:
			biggest_size = 0
			candidate = ""
			for sub in clusters[item]:
				if len(subs_dict[sub]) >= biggest_size:
					biggest_size = len(subs_dict[sub])
					candidate = sub
			centers.append(candidate)

		pprint.pprint(centers)

		cycle+=1

	return clusters	
	

def fill_tree(last_node, this_subs_dict):
	first_cluster = kmeans(this_subs_dict)
	pprint.pprint(first_cluster)
	for c in first_cluster:
		cluster_dict = {}
		cluster_dict['name'] = c
		cluster_dict['children'] = []
		if len(first_cluster[c]) < 100:
			for sub in first_cluster[c]:
				subdict = {}
				subdict['name'] = sub
				subdict['size'] = len(subs_dict[sub])
				cluster_dict['children'].append(subdict)
		else:
			new_subs_dict = {}
			for sub in first_cluster[c]:
				new_subs_dict[sub] = subs_dict[sub]
			fill_tree(cluster_dict, new_subs_dict)
		last_node['children'].append(cluster_dict)

tree = {}
tree['name'] = 'reddit'
tree['children'] = []

this_subs_dict = {}

for sub in subs_dict:
	if sub in defaults_list: continue
	if len(subs_dict[sub]) > users_threshold: this_subs_dict[sub] = subs_dict[sub]

fill_tree(tree, this_subs_dict)

json.dump(tree, outfile, indent=4)



