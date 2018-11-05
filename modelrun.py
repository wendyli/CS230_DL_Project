from CGvsPhoto import Model
import os

def main():
    
    # Fix Config so that it uses the current users
    # working directory
    cwd = os.getcwd()
    config = open('config.ini', 'r+')
    config.truncate(0) # need '0' when using r+
    config.write('[Config1]\n')
    config.write('dir_ckpt = ' + cwd + '/weights/\n')
    config.write('dir_summaries = ' + cwd + '/summaries/\n')
    config.write('dir_visualization = ' + cwd + '/visualization/\n')
    config.close()


    # Enter the database you are working with
    database = input("Enter your database (Don't forget to add quotes ;-): ")
    assert isinstance(database, str)
    database = database + '/'
    patched_database = 'Patched' + database

    
    retrain = input("Should we retrain the model? Enter 1/0: ")
    assert isinstance(retrain, int)
    
    newVersion = input("Should we use the new version of the model? Enter 1/0: ")
    

    # Create the model based on the *Patched* data
    print('Creating Model.....')
    model = Model(database_path = patched_database, image_size = 100,
                  config = 'Config1', filters = [32, 64],
                  feature_extractor = 'Stats', batch_size = 50,
                  new_version = newVersion)

    return
                  
    if retrain > 0:
        print('Training Model....')
        model.train(nb_train_batch = 1500,
                    nb_test_batch = 80,
                    nb_validation_batch = 40)

    
    # You must test on the FULL IMAGE version of the database
    print('Testing Model...')
    test_data_path = database + '/test/'
    model.test_total_images(test_data_path = test_data_path,
                            nb_images = 720, decision_rule = 'weighted_vote')


if __name__== "__main__":
    main()
