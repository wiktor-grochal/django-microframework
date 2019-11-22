def create_model_name_list(models):
    model_name_list = []
    for model in models:
        model_name_list.append(model.__name__)
    return model_name_list


def _model_has_relations(model):
    model_fields = model._meta.get_fields()
    for model_field in model_fields:
        if model_field.__class__.__name__ in ['ForeignKey', 'TreeForeignKey'] and not model_field.related_model == model:
            return True
    return False


def _model_has_rel_to(model, sorted_models):
    model_fields = model._meta.get_fields()
    for model_field in model_fields:
        if model_field.__class__.__name__ in ['ForeignKey', 'TreeForeignKey']:
            related_model = model_field.related_model
            if related_model in sorted_models:
                return True
    return False

def get_model_relations(model, sorted_models):
    model_fields = model._meta.get_fields()
    for model_field in model_fields:
        if model_field.__class__.__name__ in ['ForeignKey', 'TreeForeignKey']:
            related_model = model_field.related_model
            if related_model in sorted_models:
                return True
    return False


def sort_models_by_relations(models, sorted_models=None):
    if not models:
        return sorted_models

    if not sorted_models:
        _sorted = []
        _unsorted = []
        for model in models:
            if not _model_has_relations(model):
                _sorted.append(model)
            else:
                _unsorted.append(model)
    else:
        _sorted = sorted_models
        _unsorted = models

    for model in _unsorted:
        if _model_has_rel_to(model, _sorted):
            _sorted.append(model)
            _unsorted.remove(model)
    return sort_models_by_relations(_unsorted, _sorted)
