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


def get_field_by_name(name, model):
    model_meta_fields = model._meta.fields
    for field in model_meta_fields:
        if field.name == name:
            return field
    return None


def transform_serialized_foreign_fields(fields, model):
    fields_transformed = {}
    for field_name, field_value in fields.items():
        field = get_field_by_name(field_name, model)
        if field:
            field_type = field.get_internal_type()
            if field_type in ['ForeignKey', 'TreeForeignKey']:
                fields_transformed[f'{field_name}_id'] = field_value
            else:
                fields_transformed[field_name] = field_value
    return fields_transformed
