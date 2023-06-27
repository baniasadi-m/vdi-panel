from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VDISerializer
from ...models import VirtualDesktop

@api_view(['GET'])
def api_vdesktops(request):
    if request.method == 'GET':
        vds = VirtualDesktop.objects.all()
        serializer = VDISerializer(vds,many=True)
        return Response(serializer.data)
