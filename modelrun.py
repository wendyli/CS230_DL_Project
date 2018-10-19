from CGvsPhoto import Model

print 'Creating Model.....'
model = Model(database_path = 'PatchedDatabase', image_size = 100,
              config = 'Config1', filters = [32, 64],
              feature_extractor = 'Stats', batch_size = 50)

#print 'Training Model....'
#model.train(nb_train_batch = 1500,
#            nb_test_batch = 80,
#            nb_validation_batch = 40)

print 'Testing Model...'
test_data_path = '/Users/Chris/Desktop/CS230/Projects/CGvsPhoto/PatchedDatabase/test/'
model.test_total_images(test_data_path = test_data_path,
                        nb_images = 720, decision_rule = 'weighted_vote')
