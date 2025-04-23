import os
import pandas as pd
import logging

def save_to_report(report_name: str, headers: list, data_list: list):
    DEFAULT_REPORT_DIR = "reports"

    if not os.path.exists(DEFAULT_REPORT_DIR):
        os.makedirs(DEFAULT_REPORT_DIR)
    try:
        csv_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.csv")
        xlsx_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.xlsx")
    except Exception as e:
        logging.warning(f"[警告] 解析報告路徑錯誤: {e}", exc_info=True)
    new_data = pd.DataFrame(data_list).reindex(columns=headers)

    try:
        if os.path.exists(csv_path):
            old_data = pd.read_csv(csv_path)
            combined = pd.concat([old_data, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
        # logging.info(f"[儲存] CSV報告 成功: {csv_path}")
    except Exception as e:
        logging.error(f"[錯誤] CSV儲存錯誤: {e}", exc_info=True)

    try:
        if os.path.exists(xlsx_path):
            old_data = pd.read_excel(xlsx_path)
            combined = pd.concat([old_data, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_excel(xlsx_path, index=False)
        # logging.info(f"[儲存] Excel報告 成功: {xlsx_path}")
    except Exception as e:
        logging.error(f"[錯誤] Excel儲存錯誤: {e}", exc_info=True)