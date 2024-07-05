def standard_product_dict(item, **kwargs):
    data = {
        'product_id': item.product_config_id.product_id.pk,
        'product_name': item.product_config_id.product_id.name,
        'product_config_id': item.product_config_id.pk,
        'product_img_thumb': item.product_config_id.product_id.product_img_thumb,
        'product_weight_type': item.product_config_id.product_id.weight_type,
        'product_weight': item.product_config_id.product_id.weight,
        'product_dim_h': item.product_config_id.product_id.dimension_h,
        'product_dim_l': item.product_config_id.product_id.dimension_l,
        'product_dim_w': item.product_config_id.product_id.dimension_w,
        'variation_id': item.product_config_id.variation_id.pk,
        'variation_value': item.product_config_id.variation_id.variation_value,
    }
    data.append(kwargs)
    return data