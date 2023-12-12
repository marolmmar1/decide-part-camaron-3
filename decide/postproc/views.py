from rest_framework.views import APIView
from rest_framework.response import Response
from postproc.models import PostProcessing


class PostProcView(APIView):

    def post(self, request):
        """
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
         * total_seats: int
         * voting_id: int
         * question_id: int
         * type: str
        """

        opts = request.data.get("options")
        total_seats = request.data.get("total_seats")
        voting_id = request.data.get("voting_id")
        question_id = request.data.get("question_id")
        type = request.data.get("type")

        try:
            postproc = PostProcessing.objects.get(voting_id=voting_id)
        except PostProcessing.DoesNotExist:
            postproc = PostProcessing.objects.create(
                voting_id=voting_id,
                question_id=question_id,
                type=type,
            )

        postproc.do(opts, total_seats)

        if not postproc.results:
            return Response({}, status=400)
        else:
            return Response(postproc.results)
