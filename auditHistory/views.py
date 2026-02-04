from django.http import JsonResponse

def update_audit(request):
    return JsonResponse({"message": "update_audit working"})

def get_history(request):
    return JsonResponse({"message": "get_history working"})
