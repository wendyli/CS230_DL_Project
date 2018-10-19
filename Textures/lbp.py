import numpy as np 
from CGvsPhoto import image_loader as il

from multiprocessing import Pool

from functools import partial

from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import normalize
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_curve


import xgboost as xgb

import cv2

import time

import os

import pickle

def compute_code(minipatch, mode = 'ltc'): 

	s = np.sign(minipatch - minipatch[1,1])
	# print(s)
	if mode == 'lbp':
		s[s == -1] = 0
		# print(s)
		# code_1_clock = time.clock()
		binary = array_to_bin(s)
		# code_1_dur = time.clock() - code_1_clock
		# print('Binary computation time : ' + str(code_1_dur) + 'ms')
		# print(binary)

		return(binary)
	if mode == 'ltc': 
		return((str(int(np.sum(s[s==1])))+ 'u', str(-int(np.sum(s[s == -1]))) + 'l'))
	# return('0b100000000')

def get_classes(mode = 'ltc'):
	classes = dict()
	if mode == 'lbp':
		n = 0
		for i in range(256):
			b = '{:08b}'.format(i)
			A = [[int(b[0]), int(b[1]), int(b[2])], 
				 [int(b[7]), 0, int(b[3])],
				 [int(b[6]), int(b[5]), int(b[4])]]

			b = array_to_bin(np.array(A))
			# print(b)
			if b not in classes:
				classes[b] = n
				n+=1 
		
	if mode == 'ltc': 
		n = 0
		for i in range(9):
			classes[str(i) + 'l'] = n
			classes[str(i) + 'u'] = n + 1
			n+=2

	print(str(n) + ' classes')
	return(classes)

def compute_error_image(image): 
	prediction = np.zeros([image.shape[0], image.shape[1], image.shape[2]])
	for k in range(image.shape[2]):
		for i in range(image.shape[0]-1):
			for j in range(image.shape[1]-1):
				a = image[i, j+1, k] 
				b = image[i+1, j, k]
				c = image[i+1, j+1, k]

				if c <= min(a,b):
					prediction[i,j,k] = max(a,b)
				else: 
					if c >= max(a,b):
						prediction[i,j,k] = min(a,b)
					else: 
						prediction[i,j,k] = a + b -c
	# print(prediction.shape)
	# print(image.shape)
	error = image - prediction 
	# print(error.shape)
	return(error)

def array_to_bin(A): 


	T = np.array([A[0,0], A[0,1], A[0,2], A[1,2], A[2,2],
			 A[2,1], A[2,0], A[1,0]])


	nb_c = np.sum(np.abs(T[:7] - T[1:]))


	T = T.astype(np.uint8)


	if nb_c > 2: 
		binary = 5
	else: 
		binary = np.packbits(T)[0]
		# binary = T[0]
		# binary += T[1]<<1
		# binary += T[2]<<2
		# binary += T[3]<<3
		# binary += T[4]<<4
		# binary += T[5]<<5
		# binary += T[6]<<6
		# binary += T[7]<<7

	return(binary)

def compute_jpeg_coef(image): 

	height = image.shape[1]
	width = image.shape[0]
	nb_channels = image.shape[2]
	result = np.zeros([8*int(width/8), 8*int(height/8), nb_channels], dtype = np.float32)

	for c in range(nb_channels):
		for i in range(int(width/8)):
			for j in range(int(height/8)): 
				result[8*i:8*(i+1), 8*j:8*(j+1), c] = np.round(cv2.dct(np.float32((image[8*i:8*(i+1), 8*j:8*(j+1), c])-128)))
				# print(np.max(result[8*i:8*(i+1), 8*j:8*(j+1), c]))
	return(result)

def compute_hist(image, mode = 'ltc'): 

	hist_1 = dict()
	hist_2 = dict()
	hist_error_1 = dict()
	hist_error_2 = dict()
	for i in classes.keys():
		hist_1[i] = 0
		hist_2[i] = 0
		hist_error_1[i] = 0
		hist_error_2[i] = 0

	image = cv2.cvtColor(image*255, cv2.COLOR_RGB2YCR_CB)
	# image = compute_jpeg_coef(image)
	# error_clock = time.clock()
	error = compute_error_image(image)
	# error_dur = time.clock() - error_clock

	# print('Error image computation time : ' + str(error_dur) + 'ms')
	# code_1_dur = 0
	for i in range(1, image.shape[0] - 2): 
		for j in range(1, image.shape[1] - 2): 
			if mode == 'lbp':
				# code_1_clock = time.clock()
				b = compute_code(image[i-1:i+2, j-1:j+2,0], mode)
				hist_1[b] += 1
				# code_1_dur += time.clock() - code_1_clock
				b = compute_code(image[i-1:i+2, j-1:j+2,1], mode)
				hist_2[b] += 1
				# b = compute_code(error[i-1:i+2, j-1:j+2,0], mode)
				# hist_error_1[b] += 1
				# b = compute_code(error[i-1:i+2, j-1:j+2,1], mode)
				# hist_error_2[b] += 1

			if mode == 'ltc':
				b = compute_code(image[i-1:i+2, j-1:j+2,0], mode)
				hist_1[b[0]] += 1
				hist_1[b[1]] += 1
				b = compute_code(image[i-1:i+2, j-1:j+2,1], mode)
				hist_2[b[0]] += 1
				hist_2[b[1]] += 1				
			# b_error = compute_code(error[i-1:i+2, j-1:j+2])
			# hist_error[b_error] += 1

	# print('Code 1 computation time : ' + str(code_1_dur/((image.shape[0] - 3)*(image.shape[1] - 3))) + 'ms')

	F = []
	N = (image.shape[0] - 3)*(image.shape[1] - 3)
	for i in hist_1.keys():
		F.append(hist_1[i]/N)
		F.append(hist_2[i]/N)
		# F.append(hist_error_1[i]/N)
		# F.append(hist_error_2[i]/N)

	return(np.array(F))


def compute_features(data, i, batch_size, nb_batch, mode = 'ltc'): 

	# print('Compute features for batch ' + str(i+1) + '/' + str(nb_batch))
	images, labels = data[0], data[1]
	features = []
	y_train = []
	features.append(compute_hist(images, mode))
	y_train.append(labels[0])

	# print(features[0])
	return(features, y_train)

def compute_features_par(image, pool, mini_size = 100, mode = 'lbp'): 

	# print(image.shape)
	width = image.shape[1]
	height = image.shape[0]
	images = []
	for i in range(int(height/mini_size)): 
		for j in range(int(width/mini_size)):
			images.append(image[i:i+mini_size, j:j+mini_size])

	result = pool.map(partial(compute_hist,
							  mode = mode),
							  images) 

	features = result[0]

	for i in range(1, len(result)): 
		features += result[i]

	features /= len(result)

	return(features)


def compute_testing_features(i, batch_size, nb_test_batch, data): 

	print('Compute features for testing batch ' + str(i+1) + '/' + str(nb_test_batch))
	images, labels = data.get_batch_test(batch_size = batch_size,
												 crop = False)

	features = []
	y_test = []
	for i in range(batch_size): 
		features.append(compute_hist(images))
		y_test.append(labels[0])

	return(features, y_test)


def test_total_images(test_data_path, nb_images, classifier,
					  minibatch_size = 25, decision_rule = 'majority_vote',
					  only_green = False): 
	"""Performs boosting for classifying full-size images.
	Decomposes each image into patches (with size = self.image_size), computes the posterior probability of each class
	and uses a decision rule to classify the full-size image.
	"""
	valid_decision_rule = ['majority_vote', 'weighted_vote']
	if decision_rule not in valid_decision_rule:
		raise NameError(decision_rule + ' is not a valid decision rule.')

	print('	 Testing for the database : ' + test_data_path)

	data_test = il.Test_loader(test_data_path, subimage_size = 100, only_green = only_green)


	pool = Pool()
	tp = 0
	fp = 0
	nb_CGG = 0
	accuracy = 0
	for i in range(nb_images):
		batch, label, width, height, original, image_file = data_test.get_next_image()
		batch_size = batch.shape[0]
		j = 0
		prediction = 0
		labels = []
		diff = []
		nb_im = 0
		while j < batch_size:

			dat = []
			for k in range(j, min(j+minibatch_size, batch_size)): 
				dat.append([batch[k], label])

			to_compute = [i for i in range(minibatch_size)]
			result = pool.starmap(partial(compute_features, 
										batch_size = 1, 
										nb_batch = minibatch_size, 
										mode = 'lbp'),
										zip(dat, to_compute)) 
			res = []
			for k in range(len(result)):
				res.append(result[k][0][0])
			res = normalize(np.array(res), axis = 1)
			pred = np.log(classifier.predict_proba(res) + 0.00000001)
			# print(classifier.predict(np.array(res)))
					
			nb_im += pred.shape[0]
			label_image = np.argmax(pred, 1)
			d =	np.max(pred, 1) - np.min(pred, 1)
			for k in range(d.shape[0]):
				diff.append(np.round(d[k], 1))

			if decision_rule == 'majority_vote':
				prediction += np.sum(label_image)
			if decision_rule == 'weighted_vote':
				prediction += np.sum(-2*d*(label_image - 0.5))

			for l in label_image:
				labels.append(data_test.image_class[l])
			j+=minibatch_size

				 
		diff = np.array(diff)
		if decision_rule == 'majority_vote':
			prediction = data_test.image_class[int(np.round(prediction/batch_size))]
		if decision_rule == 'weighted_vote':
			prediction = data_test.image_class[int(max(prediction,0)/abs(prediction))]
				

		if label == 'CGG':
			nb_CGG += 1
		if(label == prediction):
			accuracy+= 1
			if(prediction == 'CGG'):
				tp += 1
		else:
			if prediction == 'CGG':
				fp += 1
		print(prediction, label)

		if ((i+1)%10 == 0):
			print('\n_______________________________________________________')
			print(str(i+1) + '/' + str(nb_images) + ' images treated.')
			print('Accuracy : ' + str(round(100*accuracy/(i+1), 2)) + '%')
			if tp + fp != 0:
				print('Precision : ' + str(round(100*tp/(tp + fp), 2)) + '%')
			if nb_CGG != 0:
					print('Recall : ' + str(round(100*tp/nb_CGG,2)) + '%')
			print('_______________________________________________________\n')


	print('\n_______________________________________________________')
	print('Final Accuracy : ' + str(round(100*accuracy/(nb_images), 3)) + '%')
	print('Final Precision : ' + str(round(100*tp/(tp + fp), 3)) + '%')
	print('Final Recall : ' + str(round(100*tp/nb_CGG, 3)) + '%')
	print('_______________________________________________________\n')



if __name__ == '__main__': 

	data_directory = '/work/smg/v-nicolas/level-design_raise_Q60/'
	image_size = None

	data = il.Database_loader(directory = data_directory, 
								size = image_size, only_green = False)

	mode = 'lbp'

	classes = get_classes(mode)


	dump_data_directory = "/work/smg/v-nicolas/data_lbp/"
	save_data = input('Save training data? (y/N) : ')

	if save_data == 'y':
		save_data = True
		load_data = None
		dump_name = input('Name of the dump file : ')
	else: 
		save_data = False
		load_data = input('Load data? (y/N) : ')
		if load_data == 'y':
			load_data = input('File to load (source directory : ' + dump_data_directory + ') : ')
		else: 
			load_data = None		
	
	batch_size = 1
	nb_hist = 2
	pool = Pool()
	
	if load_data is None:

		nb_train_batch = 2520
		

		

		print('Training...')
		features_train = np.empty([nb_train_batch*batch_size, nb_hist*len(classes.keys())])
		y_train = np.empty([nb_train_batch*batch_size,])

			
		index = 0
		for i in range(nb_train_batch):
			data_train = []
			print('Getting batch ' + str(i+1) + '/' + str(nb_train_batch))
			for j in range(batch_size):
				# print('Getting image ' + str(j+1) + '/' + str(batch_size))
				images_batch, y_batch = data.get_next_train(crop = False)
				data_train.append([images_batch, y_batch])
				print(images_batch.shape)
				features_train[i] = compute_features_par(images_batch, pool, mode = mode)
				y_train[i] = y_batch[0]
		

			# to_compute = [i for i in range(batch_size)]
			# result = pool.starmap(partial(compute_features, 
			# 							batch_size = 1, 
			# 							nb_batch = batch_size, 
			# 							mode = mode),
			# 							zip(data_train, to_compute)) 



		

			
			# for i in range(len(result)):
			# 	features_train[index:index+1] = result[i][0]
			# 	y_train[index:index+1] = result[i][1]

			# 	index+=1

		del(data_train)
		# del(result)

		features_train = normalize(features_train, axis = 1)
		print(features_train[0], y_train[0])
		print(features_train[1], y_train[1])
		print(features_train[2], y_train[2])

		if save_data: 
			pickle.dump((features_train, y_train), open(dump_data_directory + dump_name + 'train.pkl', 'wb'))

	else: 
		features_train, y_train = pickle.load(open(dump_data_directory + load_data + 'train.pkl', 'rb'))

	# clf = SVC()

	# clf = SVC(kernel = 'linear', probability = True)

	clf = CalibratedClassifierCV(LinearSVC())

	# clf = xgb.XGBClassifier(max_depth = 3, learning_rate = 0.1, 
	# 						n_estimators = 150)


	print('Fitting Classifier...')

	clf.fit(features_train, y_train)

	y_pred = clf.predict(features_train)

	score = accuracy_score(y_pred,y_train)

	print("Accuracy : " + str(score))



	print('Testing...')


	nb_test_batch = 720

	if load_data is None:
		features_test = np.empty([nb_test_batch*batch_size, nb_hist*len(classes.keys())])
		y_test = np.empty([nb_test_batch*batch_size,])



		data_test = []
		index = 0
		for i in range(nb_test_batch):
			print('Getting batch ' + str(i+1) + '/' + str(nb_test_batch))
			for j in range(batch_size):
				# print('Getting image ' + str(j+1) + '/' + str(batch_size))
				images_batch, y_batch = data.get_next_test(crop = False)
				data_test.append([images_batch, y_batch])
				print(images_batch.shape)
				features_test[i] = compute_features_par(images_batch, pool, mode = mode)
				y_test[i] = y_batch[0]
		

			# to_compute = [i for i in range(batch_size)]
			# result = pool.starmap(partial(compute_features, 
			# 							batch_size = 1, 
			# 							nb_batch = batch_size, 
			# 							mode = mode),
			# 							zip(data_test, to_compute)) 
			# for i in range(len(result)):
			# 	features_test[index:index+1] = result[i][0]
			# 	y_test[index:index+1] = result[i][1]

			# 	index+=1


		del(data_test)



		# del(result)

		features_test = normalize(features_test, axis = 1)
		print(features_test[0], y_test[0])
		print(features_test[1], y_test[1])
		print(features_test[2], y_test[2])

		if save_data: 
			pickle.dump((features_test, y_test), open(dump_data_directory + dump_name + 'test.pkl', 'wb'))

	else: 
		load_data = input('File to load (source directory : ' + dump_data_directory + ') : ')
		features_test, y_test = pickle.load(open(dump_data_directory + load_data + 'test.pkl', 'rb'))


	print('Prediction...')
	y_pred = clf.predict(features_test)

	scores = clf.predict_proba(features_test)[:,1]

	print(scores.shape)

	score = accuracy_score(y_pred,y_test)

	print("Accuracy : " + str(score))

	fpr, tpr, _ = roc_curve(y_test, scores)

	test_name = input('Test name : ')

	filename = '/home/smg/v-nicolas/ROC/' + test_name + '.pkl'
	print('Saving tpr and fpr in file : ' + filename)
	pickle.dump((fpr, tpr), open(filename, 'wb'))

	# test_data_total = "/work/smg/v-nicolas/level-design_raise/test/"

	# test_total_images(test_data_total, 720, clf, decision_rule = 'weighted_vote')