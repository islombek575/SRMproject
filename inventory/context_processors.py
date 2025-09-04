def user_roles(request):
    user = request.user
    is_superuser = user.is_superuser if user.is_authenticated else False
    is_cashier = user.groups.filter(name='cashier').exists() and not is_superuser if user.is_authenticated else False
    return {
        'is_superuser': is_superuser,
        'is_cashier': is_cashier
    }
