from CGvsPhoto import Model

def main():

    # Enter the database you are working with
    database = input("Enter your database (Don't forget to add quotes ;-): ")
    assert isinstance(database, str)
    database = database + '/'

    
    retrain = input("Should we retrain the model? 1/0 ")
    assert isinstance(retrain, int)
    

    print 'Creating Model.....'
    model = Model(database_path = database, image_size = 100,
                  config = 'Config1', filters = [32, 64],
                  feature_extractor = 'Stats', batch_size = 50)

    if retrain > 0:
        print 'Training Model....'
        model.train(nb_train_batch = 1500,
                    nb_test_batch = 80,
                    nb_validation_batch = 40)

    print 'Testing Model...'
    test_data_path = database + '/test/'
    model.test_total_images(test_data_path = test_data_path,
                            nb_images = 720, decision_rule = 'weighted_vote')


if __name__== "__main__":
    main()
