import os


def photo_upload_path(instance, filename):
    safe_chain_name = ''.join(
        c for c in instance.trading_client.name if c.isalnum() or c in (
            ' ', '-', '_'
        )
    ).rstrip()
    safe_category_name = ''.join(
        c for c in instance.category.name if c.isalnum() or c in (
            ' ', '-', '_'
        )
    ).rstrip()
    if instance.is_competitor:
        brand_folder = os.path.join(instance.brand.name, 'competitor')
    else:
        brand_folder = instance.brand.name
    file_ext = os.path.splitext(filename)[1]
    return os.path.join(
        'photo_reports',
        str(instance.created_at.year),
        f'{instance.created_at.month:02d}',
        safe_chain_name,
        safe_category_name,
        brand_folder,
        f'{instance.id}{file_ext}'
    )
