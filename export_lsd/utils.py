import os
import zipfile

from export_lsd.models import Formato931

NOT_SIJP = [27, 48, 99]
NOT_OS_INSSJP = [27, 99]


def get_value_from_txt(txt_line: str, field_name: str) -> str:
    resp = ''

    qs = Formato931.objects.get(name=field_name)
    if qs:
        resp = txt_line[qs.fromm-1:qs.fromm + qs.long-1]

    return resp


def amount_txt_to_integer(amount_txt: str, mulitp=100) -> int:
    resp = float(amount_txt.replace(',', '.')) * mulitp
    resp = int(resp)

    return resp


def amount_txt_to_float(amount_txt: str, mulitp=100) -> float:
    resp = float(amount_txt.replace(',', '.')) * mulitp
    resp = float(resp)

    return resp


def exclude_eventuales(txt_info: str) -> str:
    resp = []
    for legajo in txt_info:
        mod_cont = int(get_value_from_txt(legajo, 'Código de Modalidad de Contratación'))
        if mod_cont != 102:
            resp.append(legajo)

    return resp


def just_eventuales(txt_info: str) -> str:
    resp = []
    for legajo in txt_info:
        mod_cont = int(get_value_from_txt(legajo, 'Código de Modalidad de Contratación'))
        if mod_cont == 102:
            resp.append(legajo)

    return resp


def sync_format(info: str, expected_len: int, type_info: str) -> str:
    resp = info

    if len(info) != expected_len or ',' in info:
        if len(info) > expected_len:
            resp = round(float(info.replace(',', '.').strip()))
            resp = str(resp).zfill(expected_len)
        else:
            if type_info == 'NU':
                resp = str(int(float(info.replace(',', '.').strip()) * 100))
                resp = resp.zfill(expected_len)
            else:
                resp = info.ljust(expected_len)

    return resp


def file_compress(inp_file_names, out_zip_file):
    """
    function : file_compress
    args : inp_file_names : list of filenames to be zipped
    out_zip_file : output zip file
    return : none
    assumption : Input file paths and this code is in same directory.
    """
    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED
    print(f" *** Input File name passed for zipping - {inp_file_names}")

    # create the zip file first parameter path/name, second mode
    print(f' *** out_zip_file is - {out_zip_file}')
    zf = zipfile.ZipFile(out_zip_file, mode="w")

    try:
        for file_to_write in inp_file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            file_to_write_name = file_to_write.split('/')[-1]
            print(f' *** Processing file {file_to_write_name}')
            zf.write(file_to_write, file_to_write_name, compress_type=compression)

    except FileNotFoundError as e:
        print(f' *** Exception occurred during zip process - {e}')
    finally:
        # Don't forget to close the file!
        zf.close()


def delete_list_of_liles(list_to_delete: list):
    for f in list_to_delete:
        fname = f.rstrip()
        if os.path.isfile(fname):
            os.remove(fname)
