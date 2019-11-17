def create_model_name_list(models):
    model_name_list = []
    for model in models:
        model_name_list.append(model.__name__)
    return model_name_list
