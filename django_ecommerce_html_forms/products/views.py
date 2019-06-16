from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB using the Product model
    products = Product.objects.filter(active=True)  # <YOUR CODE HERE>

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = Product.objects.filter(featured=True).order_by('?')[:4]  # <YOUR CODE HERE>

    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_products}
    )


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        context = {'categories': categories}
        return render(request, 'create_product.html', context)  # static_form is just used as an example
    elif request.method == 'POST':
        fields = ['name', 'sku', 'price']
        errors = {}
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'

        if errors:
            return render(
                request, 
                'create_product.html', 
                context={
                    'categories': categories, 
                    'errors': errors, 
                    'payload': request.POST
                }
            )
        
        
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "SKU must contain 8 alphanumeric characters."
            
        # Price validation: positive float lower than 10000.00
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99:
            error['price'] = "Price can't be negative or greater than $9999.9"

        if errors:
            return render(
                request, 
                'create_product.html', 
                context={
                    'categories': categories, 
                    'errors': errors, 
                    'payload': request.POST
                }
            )

        
        category = Category.objects.get(name=request.POST.get('category'))  # <YOUR CODE HERE>
        product = Product.objects.create(
            name=request.POST.get('name'),
            sku=request.POST.get('sku'),
            price=float(request.POST.get('price')),
            description=request.POST.get('description', ''),
            category=category
        )  # <YOUR CODE HERE>

        # Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        images = []
        for i in range(3):
            image = request.POST.get('image_{}'.format(i + 1))
            if image:
                images.append(image)
                
        for image in images:
            ProductImage.objects.create(
                product=product, 
                url=image
            )
        return redirect('products')


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)

    # Get all categories from the DB
    categories = Category.objects.all()
    if request.method == 'GET':
        return render(
            request, 
            'edit_product.html', 
            context={
                'product': product,
                'categories': categories,
                'images': [image.url for image in product.productimage_set.all()]
            }
        ) 
    elif request.method == 'POST':
        fields = ['name', 'sku', 'price']
        errors = {}
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'
        
        if errors:
            return render(
                request,
                'edit_product.html',
                context={
                    'product': product,
                    'categories': categories,
                    'errors': errors,
                    'payload': request.POST
                }
            )
        
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."
            
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "SKU must contain 8 alphanumeric characters."
            
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99:
            errors['price'] = "Price can't be negative or greater than $9999.9"
            
        if errors:
            return render(
                request,
                'edit_product.html',
                context={
                    'product': product,
                    'categories': categories,
                    'errors': errors,
                    'payload': request.POST
                }
            )
            
        product.name = request.POST.get('name')
        product.sku = request.POST.get('sku')
        product.price = float(request.POST.get('price'))
        product.description = request.POST.get('description')

        # Get proper category from the DB based on the category name given in
        # payload. Update product category.
        category = Category.objects.get(name=request.POST.get('category'))
        product.category = category
        product.save()

        new_images = []
        for i in range(3):
            image = request.POST.get('image_{}'.format(i + 1))
            if image:
                new_images.append(image)
                
        old_images = [image.url for image in product.productimage_set.all()]
        
        images_to_delete = []
        for image in old_images:
            if image not in new_images:
                images_to_delete.append(image)
        ProductImage.objects.filter(url__in=images_to_delete).delete()
        
        for image in new_images:
            if image not in old_images:
                ProductImage.objects.create(
                    product=product,
                    url=image
                )
        return redirect('products')


def delete_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>
    if request.method == 'GET':
        context={'product': product}
        return render(request, 'delete_product.html', context)  # <YOUR CODE HERE>
    elif request.method == "POST":
        product.delete()
        return redirect('products')  # <YOUR CODE HERE>


def toggle_featured(request, product_id):
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>
    product.featured = not product.featured
    product.save()
    return redirect('products')
