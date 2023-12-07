from rest_framework.views import APIView
from rest_framework.response import Response
from postproc.models import PostProcessing


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)

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

        postproc = PostProcessing.objects.create(
            voting_id=voting_id,
            question_id=question_id,
            type=type,
        )

        postproc.do(opts, total_seats)

        if not postproc.results:
            return Response({}, status=400)
        else:
            return Response({postproc.type: postproc.results})
