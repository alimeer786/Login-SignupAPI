from .models import acessDB
from rest_framework import serializers

class acessDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = acessDB
        fields = '__all__'



class UpdateAcessDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = acessDB
        fields = [
            'p_no',
            'e_tag',
            'rev',
            'issue',
            'vol',
            'qty',
            'element',
            'casting',
            'mix',
            'do',
            'transporter',
            'qc',
            'delivery',
            'erection',
            'first_ir',
            'ir_app',
            'second_ir',
            'second_app',
            'pa',
            'tr_no'
        ]

    def update(self, instance, validated_data):
        instance.p_no = validated_data.get('p_no', instance.p_no)
        instance.e_tag = validated_data.get('e_tag', instance.e_tag)
        instance.rev = validated_data.get('rev', instance.rev)
        instance.issue = validated_data.get('issue', instance.issue)
        instance.vol = validated_data.get('vol', instance.vol)
        instance.qty = validated_data.get('qty', instance.qty)
        instance.element = validated_data.get('element', instance.element)
        instance.casting = validated_data.get('casting', instance.casting)
        instance.mix = validated_data.get('mix', instance.mix)
        instance.do = validated_data.get('do', instance.do)
        instance.transporter = validated_data.get('transporter', instance.transporter)
        instance.qc = validated_data.get('qc', instance.qc)
        instance.delivery = validated_data.get('delivery', instance.delivery)
        instance.erection = validated_data.get('erection', instance.erection)
        instance.first_ir = validated_data.get('first_ir', instance.first_ir)
        instance.ir_app = validated_data.get('ir_app', instance.ir_app)
        instance.second_ir = validated_data.get('second_ir', instance.second_ir)
        instance.second_app = validated_data.get('second_app', instance.second_app)
        instance.pa = validated_data.get('pa', instance.pa)
        instance.tr_no = validated_data.get('tr_no', instance.tr_no)

        instance.save()
        return instance
