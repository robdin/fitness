"""Local LJ Speech synthesis via OpenVINO; no ONNX Runtime or network calls.

Uses Piper's installed eSpeak bridge for pronunciation and an explicitly
provided ONNX voice file for inference. Model weights are not downloaded here.
"""
import importlib.metadata
import importlib.util
import json,re,unicodedata
from pathlib import Path
import numpy as np

class LocalVoice:
    def __init__(self,model_path):
        # Persist a declined diagnostics preference without sending an opt-out
        # event. This is the package's local preference API, not a network API.
        from openvino_telemetry.utils.opt_in_checker import OptInChecker,ConsentCheckResult
        checker=OptInChecker()
        if not checker.update_result(ConsentCheckResult.DECLINED):
            raise RuntimeError('Could not disable optional inference diagnostics')
        import openvino as ov
        path=Path(model_path)
        self.config=json.loads(Path(str(path)+'.json').read_text())
        core=ov.Core()
        self.compiled=core.compile_model(core.read_model(str(path)),'CPU',{
            'INFERENCE_NUM_THREADS':2,
            'INFERENCE_PRECISION_HINT':'f32',
            'EXECUTION_MODE_HINT':'ACCURACY'
        })
        package=importlib.metadata.distribution('piper-tts')
        bridge_path=Path(package.locate_file('piper/espeakbridge.so'))
        spec=importlib.util.spec_from_file_location('espeakbridge',bridge_path)
        self.bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.bridge)
        self.bridge.initialize(str(bridge_path.parent/'espeak-ng-data'))
        self.bridge.set_voice(self.config['espeak']['voice'])

    def synthesize_wav(self,text,wav_file):
        wav_file.setnchannels(1);wav_file.setsampwidth(2);wav_file.setframerate(self.config['audio']['sample_rate'])
        sentences=[];phones=[]
        for value,punctuation,ends in self.bridge.get_phonemes(text):
            value=re.sub(r'\([^)]+\)','',value)+punctuation
            if punctuation in (',',':',';'):value+=' '
            phones.extend(unicodedata.normalize('NFD',value))
            if ends:sentences.append(phones);phones=[]
        if phones:sentences.append(phones)
        mapping=self.config['phoneme_id_map'];chunks=[]
        for phones in sentences:
            ids=mapping['^']+mapping['_']
            for phone in phones:
                if phone not in mapping:raise ValueError('Unknown speech phoneme '+repr(phone))
                ids+=mapping[phone]+mapping['_']
            ids+=mapping['$']
            result=self.compiled({'input':np.array([ids],dtype=np.int64),'input_lengths':np.array([len(ids)],dtype=np.int64),'scales':np.array([.58,.99,.75],dtype=np.float32)})
            chunks.append(np.asarray(result[self.compiled.output(0)]).squeeze().copy())
        sound=np.concatenate(chunks)
        sound=sound/(float(np.max(np.abs(sound))) or 1)*.9
        wav_file.setnchannels(1);wav_file.setsampwidth(2);wav_file.setframerate(self.config['audio']['sample_rate'])
        wav_file.writeframes((np.clip(sound,-.99,.99)*32767).astype('<i2').tobytes())
