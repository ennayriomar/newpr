"""Archive integrity, hardlink extraction and traversal contracts."""
from pathlib import Path
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import download_vision_hybrid_results as downloader


class Response(io.BytesIO):
    url='https://raw.githubusercontent.com/ennayriomar/newpr/test'


class DownloadTests(unittest.TestCase):
    def fixture(self):
        content=b'actual fitted feature bytes\x00\x01'
        hashes={name:hashlib.sha256(content).hexdigest() for name in ['bank/fit.npz','bank/model.npz']}
        archive=io.BytesIO()
        with tarfile.open(fileobj=archive,mode='w:gz') as tar:
            info=tarfile.TarInfo('vision_hybrid_results/bank/fit.npz');info.size=len(content)
            tar.addfile(info,io.BytesIO(content))
            info=tarfile.TarInfo('vision_hybrid_results/bank/model.npz');info.type=tarfile.LNKTYPE
            info.linkname='vision_hybrid_results/bank/fit.npz';tar.addfile(info)
            data=json.dumps(hashes).encode();info=tarfile.TarInfo('vision_hybrid_results/MANIFEST.sha256.json');info.size=len(data)
            tar.addfile(info,io.BytesIO(data))
        data=archive.getvalue();parts=[data[:len(data)//2],data[len(data)//2:]];offset=0;items=[]
        for i,value in enumerate(parts):
            items.append(dict(name=f'archive.part{i}',offset=offset,bytes=len(value),sha256=hashlib.sha256(value).hexdigest()));offset+=len(value)
        return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parts=items),parts,content

    def test_checked_download_and_hardlink_extraction(self):
        manifest,parts,content=self.fixture()
        def get(url,**kwargs):
            return Response(json.dumps(manifest).encode() if url.endswith('manifest.json') else parts[int(url[-1])])
        with tempfile.TemporaryDirectory() as directory,patch.object(downloader.urllib.request,'urlopen',side_effect=get):
            output=Path(directory)/'study.tar.gz';downloader.download('a'*40,output,extract=True)
            root=Path(directory)/'study_extracted/vision_hybrid_results'
            self.assertEqual((root/'bank/model.npz').read_bytes(),content)
            self.assertEqual((root/'bank/model.npz').stat().st_ino,(root/'bank/fit.npz').stat().st_ino)

    def test_corrupt_part_rejected_without_final_file(self):
        manifest,parts,_=self.fixture()
        def get(url,**kwargs):
            return Response(json.dumps(manifest).encode() if url.endswith('manifest.json') else b'x'*len(parts[int(url[-1])]))
        with tempfile.TemporaryDirectory() as directory,patch.object(downloader.urllib.request,'urlopen',side_effect=get):
            output=Path(directory)/'study.tar.gz'
            with self.assertRaisesRegex(ValueError,'hash/length'):downloader.download('b'*40,output)
            self.assertFalse(output.exists());self.assertFalse(output.with_name(output.name+'.partial').exists())

    def test_paths_and_existing_destination_are_guarded(self):
        for value in ['/outside','a/../outside','a\\outside','']:
            with self.assertRaises(ValueError):downloader.safe_relative(value)
        manifest,_,_=self.fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(downloader.urllib.request,'urlopen',return_value=Response(json.dumps(manifest).encode())):
            output=Path(directory)/'existing.tar.gz';output.write_bytes(b'preserve me')
            with self.assertRaisesRegex(ValueError,'Destination exists'):downloader.download('c'*40,output)
            self.assertEqual(output.read_bytes(),b'preserve me')


if __name__=='__main__':unittest.main()
