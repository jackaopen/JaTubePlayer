"""
This will be compiled into a exe and run as admin to update ytdlp
will be placed in _internal in programfile
will not run as a dependency of the main program, but will be called by the main program when needed
"""
import os
from openpgp.composed import SignedPublicKey, DetachedSignature
import shutil
import hashlib
import tarfile
import json
from pathlib import Path
import sys

YT_DLP_PUBLIC_KEY  = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGP78C4BEAD0rF9zjGPAt0thlt5C1ebzccAVX7Nb1v+eqQjk+WEZdTETVCg3
WAM5ngArlHdm/fZqzUgO+pAYrB60GKeg7ffUDf+S0XFKEZdeRLYeAaqqKhSibVal
DjvOBOztu3W607HLETQAqA7wTPuIt2WqmpL60NIcyr27LxqmgdN3mNvZ2iLO+bP0
nKR/C+PgE9H4ytywDa12zMx6PmZCnVOOOu6XZEFmdUxxdQ9fFDqd9LcBKY2LDOcS
Yo1saY0YWiZWHtzVoZu1kOzjnS5Fjq/yBHJLImDH7pNxHm7s/PnaurpmQFtDFruk
t+2lhDnpKUmGr/I/3IHqH/X+9nPoS4uiqQ5HpblB8BK+4WfpaiEg75LnvuOPfZIP
KYyXa/0A7QojMwgOrD88ozT+VCkKkkJ+ijXZ7gHNjmcBaUdKK7fDIEOYI63Lyc6Q
WkGQTigFffSUXWHDCO9aXNhP3ejqFWgGMtCUsrbkcJkWuWY7q5ARy/05HbSM3K4D
U9eqtnxmiV1WQ8nXuI9JgJQRvh5PTkny5LtxqzcmqvWO9TjHBbrs14BPEO9fcXxK
L/CFBbzXDSvvAgArdqqlMoncQ/yicTlfL6qzJ8EKFiqW14QMTdAn6SuuZTodXCTi
InwoT7WjjuFPKKdvfH1GP4bnqdzTnzLxCSDIEtfyfPsIX+9GI7Jkk/zZjQARAQAB
tDdTaW1vbiBTYXdpY2tpICh5dC1kbHAgc2lnbmluZyBrZXkpIDxjb250YWN0QGdy
dWI0ay54eXo+iQJOBBMBCgA4FiEErAy75oSNaoc0ZK9OV89lkztadYEFAmP78C4C
GwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQV89lkztadYEVqQ//cW7TxhXg
7Xbh2EZQzXml0egn6j8QaV9KzGragMiShrlvTO2zXfLXqyizrFP4AspgjSn/4NrI
8mluom+Yi+qr7DXT4BjQqIM9y3AjwZPdywe912Lxcw52NNoPZCm24I9T7ySc8lmR
FQvZC0w4H/VTNj/2lgJ1dwMflpwvNRiWa5YzcFGlCUeDIPskLx9++AJE+xwU3LYm
jQQsPBqpHHiTBEJzMLl+rfd9Fg4N+QNzpFkTDW3EPerLuvJniSBBwZthqxeAtw4M
UiAXh6JvCc2hJkKCoygRfM281MeolvmsGNyQm+axlB0vyldiPP6BnaRgZlx+l6MU
cPqgHblb7RW5j9lfr6OYL7SceBIHNv0CFrt1OnkGo/tVMwcs8LH3Ae4a7UJlIceL
V54aRxSsZU7w4iX+PB79BWkEsQzwKrUuJVOeL4UDwWajp75OFaUqbS/slDDVXvK5
OIeuth3mA/adjdvgjPxhRQjA3l69rRWIJDrqBSHldmRsnX6cvXTDy8wSXZgy51lP
m4IVLHnCy9m4SaGGoAsfTZS0cC9FgjUIyTyrq9M67wOMpUxnuB0aRZgJE1DsI23E
qdvcSNVlO+39xM/KPWUEh6b83wMn88QeW+DCVGWACQq5N3YdPnAJa50617fGbY6I
gXIoRHXkDqe23PZ/jURYCv0sjVtjPoVC+bg=
=bJkn
-----END PGP PUBLIC KEY BLOCK-----
"""

class ytdlp_file_updater:
    def __init__(self,
                log_handle:object=print,
                app_data_dir: str=None):
        
        self.appdata_path = app_data_dir
        self.log_handle = log_handle
        self.file_hash_dict = {}
        self.result_json = {
            "status": "",
            "message": "",
        }
        internal_dir = Path(sys.executable).resolve().parent

        self.internal_result_json_path = os.path.join(internal_dir, 'update_result.json')
        self.ytdlp_update_path = os.path.join(self.appdata_path, 'JatubePlayer', 'ytdlp_update')
        self.ytdlpgz_path = os.path.join(internal_dir, 'yt-dlp.tar.gz')
        self.new_ytdlp_path = os.path.join(internal_dir, "new_yt-dlp")
        self.ytdlp_path = os.path.join(internal_dir, 'yt_dlp')

        self.new_ytdlpexe_path = os.path.join(internal_dir, 'new_yt-dlp.exe')
        self.ytdlpexe_path = os.path.join(internal_dir, 'yt-dlp.exe')

        self.old_ytdlpexe_path = os.path.join(internal_dir, 'yt-dlp_old.exe')
        self.old_ytdlpfolder = os.path.join(internal_dir, 'yt-dlp_old')

        self.copy_ok = False

    def _dump_result(self):
        with open(self.internal_result_json_path, 'w') as f:
            json.dump(self.result_json, f, indent=4)


    def _verify_and_process(self) -> None:
        '''
        Expects: All needed file under %appdata%/JatubePlayer/ytdlp_update
        '''
    
        hash_dict = {}
        public_key, _ = SignedPublicKey.from_armor(str(YT_DLP_PUBLIC_KEY))
        signature = DetachedSignature.from_file(os.path.join(self.ytdlp_update_path, 'SHA2-256SUMS.sig'))
        sums_path = os.path.join(self.ytdlp_update_path, 'SHA2-256SUMS')
       

        with open(sums_path, 'rb') as f:
            sums_bytes = f.read()

        try:
            signature.verify(public_key, sums_bytes)
        except Exception as error:
            raise ValueError(
                f"Signature verification failed: {error}"
            ) from error
        
        for line in sums_bytes.decode("utf-8").splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue

            expected_hash, filename = parts
            filename = filename.lstrip("*")

            hash_dict[filename] = expected_hash.lower()

        expected_tar_hash = hash_dict.get("yt-dlp.tar.gz")
        expected_exe_hash = hash_dict.get("yt-dlp.exe")
        

        with (
            open(self.ytdlpgz_path, "rb") as tar_file,
            open(self.new_ytdlpexe_path, "rb") as exe_file):

            tar_hash = hashlib.file_digest(tar_file, "sha256").hexdigest()
            exe_hash = hashlib.file_digest(exe_file, "sha256").hexdigest()

            if tar_hash != expected_tar_hash:
                raise ValueError("yt-dlp.tar.gz hash mismatch")
            if exe_hash != expected_exe_hash:
                raise ValueError("yt-dlp.exe hash mismatch")

            #seek back to the beginning of the files for extraction and copying
            tar_file.seek(0)
            exe_file.seek(0)

            with tarfile.open(fileobj=tar_file, mode='r:gz') as tar:
                tar.extractall(path=self.new_ytdlp_path,filter="data")
                shutil.rmtree(self.ytdlp_path)
                shutil.copytree(os.path.join(self.new_ytdlp_path,'yt-dlp','yt_dlp'), self.ytdlp_path)
                

            with open(self.ytdlpexe_path, "wb") as destination:
                shutil.copyfileobj(exe_file, destination)



    def _get_sha256(self,
                    file_path:str) -> str:
        with open(file_path, "rb") as file:
            return hashlib.file_digest(file, "sha256").hexdigest()

    

    def _remove_downloaded_files(self):
        if os.path.exists(self.ytdlpgz_path):
            os.remove(self.ytdlpgz_path)
            
        if os.path.exists(self.new_ytdlpexe_path):
            os.remove(self.new_ytdlpexe_path)

        if os.path.exists(self.new_ytdlp_path):
            shutil.rmtree(self.new_ytdlp_path)
        


    def restore_old_files(self):
        try:
            if os.path.exists(self.ytdlp_path):
                shutil.rmtree(self.ytdlp_path)
            shutil.copytree(self.old_ytdlpfolder,self.ytdlp_path)
            shutil.copy(self.old_ytdlpexe_path,self.ytdlpexe_path)
        except Exception as error:
            self.result_json["status"] = "error"
            self.result_json["message"] = f"Failed to restore old files: {error}"
            raise Exception(f"Failed to restore old files: {error}") from error

    def _move_to_current_directory(self):
        '''
        Move the downloaded files to the current directory
        '''
        if os.path.exists(os.path.join(self.ytdlp_update_path,'new_yt-dlp.exe')):
            shutil.copy(os.path.join(self.ytdlp_update_path,'new_yt-dlp.exe'), self.new_ytdlpexe_path)
        if os.path.exists(os.path.join(self.ytdlp_update_path,'yt-dlp.tar.gz')):
            shutil.copy(os.path.join(self.ytdlp_update_path,'yt-dlp.tar.gz'), self.ytdlpgz_path)


    def remove_old_files(self):
        if os.path.exists(self.old_ytdlpexe_path):
            os.remove(self.old_ytdlpexe_path)
        if os.path.exists(self.old_ytdlpfolder) and os.path.isdir(self.old_ytdlpfolder):
            shutil.rmtree(self.old_ytdlpfolder)

    def _copy_old_files(self):
        self.remove_old_files()
        shutil.copytree(self.ytdlp_path,self.old_ytdlpfolder)
        shutil.copy(self.ytdlpexe_path,self.old_ytdlpexe_path)




        

        

        


    def main(self):
        self._remove_downloaded_files()


        self._copy_old_files()
        self.copy_ok = True
        self._move_to_current_directory()
        self._verify_and_process()
        self.copy_ok = False
        self.remove_old_files()
        self._remove_downloaded_files()

        self.result_json["status"] = "success"
        self.result_json["message"] = "yt-dlp updated successfully"
        self._dump_result()
        

if __name__ == "__main__":
    app_data_dir = sys.argv[1]
    updater = ytdlp_file_updater(app_data_dir=app_data_dir)
    
    try:
        updater.main()
    except Exception as error:
        updater.result_json.update(
            status="error",
            message=f"Update failed: {error}",
        )

        try:
            if not updater.copy_ok:
                updater.remove_old_files()
            else:
                updater.restore_old_files()
        except Exception as rollback_error:
            updater.result_json["message"] += (
                f"; rollback failed: {rollback_error}"
            )

        updater._dump_result()
        raise SystemExit(1)
    raise SystemExit(0)
    