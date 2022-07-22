"""Test suite for compliance with the ITU-R BS.1770-4 recommendation"""
import os.path
import zipfile

import torch
import torchaudio.functional as F
from torchaudio_unittest.common_utils import load_wav, TempDirMixin, TestBaseMixin

# Test files linked in https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BS.2217-2-2016-PDF-E.pdf
_COMPLIANCE_FILE_URLS = {
    "1770-2_Comp_RelGateTest": "http://www.itu.int/dms_pub/itu-r/oth/11/02/R11020000010030ZIPM.zip",
    "1770-2_Comp_AbsGateTest": "http://www.itu.int/dms_pub/itu-r/oth/11/02/R11020000010029ZIPM.zip",
    "1770-2_Comp_24LKFS_500Hz_2ch": "http://www.itu.int/dms_pub/itu-r/oth/11/02/R11020000010018ZIPM.zip",
    "1770-2 Conf Mono Voice+Music-24LKFS": "http://www.itu.int/dms_pub/itu-r/oth/11/02/R11020000010038ZIPM.zip",
}


class Loudness(TempDirMixin, TestBaseMixin):
    def download_and_extract_file(self, filename):
        zippath = self.get_temp_path(filename + ".zip")
        torch.hub.download_url_to_file(_COMPLIANCE_FILE_URLS[filename], zippath, progress=False)
        with zipfile.ZipFile(zippath) as file:
            file.extractall(os.path.dirname(zippath))
        return self.get_temp_path(filename + ".wav")

    def test_measure_loudness_relative_gate(self):
        filepath = self.download_and_extract_file("1770-2_Comp_RelGateTest")
        waveform, sample_rate = load_wav(filepath)
        waveform = waveform.to(self.device)

        loudness = F.loudness(waveform, sample_rate)
        expected = torch.tensor(-10.0, dtype=loudness.dtype, device=self.device)
        self.assertEqual(loudness, expected, rtol=0.01, atol=0.1)

    def test_measure_loudness_absolute_gate(self):
        filepath = self.download_and_extract_file("1770-2_Comp_AbsGateTest")
        waveform, sample_rate = load_wav(filepath)
        waveform = waveform.to(self.device)

        loudness = F.loudness(waveform, sample_rate)
        expected = torch.tensor(-69.5, dtype=loudness.dtype, device=self.device)
        self.assertEqual(loudness, expected, rtol=0.01, atol=0.1)

    def test_measure_loudness_two_channels(self):
        filepath = filepath = self.download_and_extract_file("1770-2_Comp_24LKFS_500Hz_2ch")
        waveform, sample_rate = load_wav(filepath)
        waveform = waveform.to(self.device)

        loudness = F.loudness(waveform, sample_rate)
        expected = torch.tensor(-24.0, dtype=loudness.dtype, device=self.device)
        self.assertEqual(loudness, expected, rtol=0.01, atol=0.1)

    def test_measure_loudness_mono_voice_music(self):
        filepath = self.download_and_extract_file("1770-2 Conf Mono Voice+Music-24LKFS")
        waveform, sample_rate = load_wav(filepath)
        waveform = waveform.to(self.device)

        loudness = F.loudness(waveform, sample_rate)
        expected = torch.tensor(-24.0, dtype=loudness.dtype, device=self.device)
        self.assertEqual(loudness, expected, rtol=0.01, atol=0.1)