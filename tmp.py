def manage_users(request):
    users = User.objects.all()

    if request.method == "POST" and 'delete_user' in request.POST:
        user_id = request.POST.get('delete_user')
        user_to_delete = User.objects.get(id=user_id)

        if user_to_delete.role == "user":

            logger.info('User delete action', extra={
                'user': request.user,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'absolute_uri': request.build_absolute_uri(),
                'http_method': request.method,
                'attackType': 'RCE'

            })
            user_to_delete.delete()

        else:

            logger.info('Unauthorized user delete action tried.', extra={
                'user': request.user,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'absolute_uri': request.build_absolute_uri(),
                'http_method': request.method,
                'attackType': 'RCE'

            })
            pass

        return redirect('manage_users')

    return render(request, 'manage_users.html', {'users': users})


def search_feed(request):
    feed_url = request.GET.get('feed', '')
    if feed_url:
        logger.info('Feed suggestion submitted.', extra={
            'user': request.user,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'absolute_uri': request.build_absolute_uri(),
            'http_method': request.method,
            'attackType': 'PS',
            'input': feed_url

        })
        try:
            response = requests.get(feed_url)
            if response.status_code == 200:

                return JsonResponse(response.text, safe=False)
            else:

                return JsonResponse({'error': 'Failed to fetch data from the feed', 'status_code': response.status_code}, status=response.status_code)
        except requests.RequestException as e:

            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'No feed URL provided'}, status=400)


def execute_command(request):
    try:
        command = request.GET.get('command', '')

        if command:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            exit_code = process.wait()

            if exit_code == 0:
                return JsonResponse({'status': 'success', 'output': stdout.decode()})
            else:
                return JsonResponse({'status': 'error', 'output': stderr.decode()})
        else:
            return JsonResponse({'error': 'No command provided'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def getCurrency(request):
    try:

        logger.info('Currency convert attempt', extra={
            'user': request.user,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'absolute_uri': request.build_absolute_uri(),
            'http_method': request.method,
            'attackType': 'RCE'

        })
        divident = request.GET.get('from')
        divisor = request.GET.get('to')
        command = f"python3 currency.py {divident} {divisor}"
        if divident or divisor:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            exit_code = process.wait()
            if exit_code == 0:
                return JsonResponse({'result': stdout.decode()})
            else:
                return JsonResponse({'status': 'error', 'output': stderr.decode()})
        else:
            return JsonResponse({'error': 'No command provided'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
