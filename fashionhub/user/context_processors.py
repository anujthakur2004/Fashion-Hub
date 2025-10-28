def is_logged_in(request):
    return {'is_logged_in': bool(request.session.get('user_id'))}
