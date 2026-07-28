from wkcalc import *
from wkcalc.persistence import clear_autosave, last_used_folder, load_record, recover_autosave, remember_last_folder, save_record, write_autosave

def record():
    road=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=8,full_kerb_to_kerb_is_travelled=True,kerb_to_kerb_width_m=8)
    return CalculationRecord(road_input=road,result=calculate_wk(road))
def test_save_load_identical(tmp_path):
    saved=save_record(record(),tmp_path/"test.wkcalc.json"); assert load_record(tmp_path/"test.wkcalc.json")==saved
def test_autosave_recovery(tmp_path):
    saved=write_autosave(record(),tmp_path); assert recover_autosave(tmp_path)==saved; clear_autosave(tmp_path); assert recover_autosave(tmp_path) is None
def test_last_folder_is_stored_in_local_settings_json(tmp_path):
    chosen=tmp_path/"chosen";remember_last_folder(chosen,tmp_path);assert last_used_folder(tmp_path/"default",tmp_path)==chosen
