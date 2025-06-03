from google.cloud import bigquery
import pathlib

description_SQL_hoc_vien = pathlib.Path("model/prompts/description_SQL_hoc_vien.md").read_text(encoding='utf-8')

# Hàm lấy danh sách bảng trong dataset
def get_all_table_names(client: bigquery.Client, project_id: str, dataset_id: str) -> list:
    try:
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        tables = list(client.list_tables(dataset_ref))
        return [table.table_id for table in tables]
    except Exception as e:
        print(f"Lỗi khi lấy danh sách bảng: {e}") # In lỗi ra console để debug
        return [] # Trả về danh sách rỗng nếu có lỗi

# Hàm lấy schema + sample
def get_table_schema_and_sample(client: bigquery.Client, project_id: str, dataset_id: str, table_name: str, sample_rows_limit=2):
    try:
        table_ref = client.dataset(dataset_id, project=project_id).table(table_name)
        table = client.get_table(table_ref)

        # Lấy schema
        schema_string = f"CREATE TABLE `{project_id}.{dataset_id}.{table_name}` (\n" # Thêm project_id và dataset_id
        for field in table.schema:
            schema_string += f"\t`{field.name}` {field.field_type}"
            # Không cần thêm (REPEATED) hay (NULLABLE) vì field_type đã bao hàm
            # và mode không phải là một phần của cú pháp CREATE TABLE chuẩn theo cách này.
            # BigQuery tự xử lý NULLABLE mặc định. REPEATED là một kiểu cấu trúc.
            schema_string += ",\n" # Giữ dấu phẩy ở cuối mỗi dòng
        schema_string = schema_string.rstrip(",\n") + "\n);" # Xóa dấu phẩy cuối cùng và đóng ngoặc

        # Lấy dữ liệu mẫu
        query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` LIMIT {sample_rows_limit}"

        query_job = client.query(query)
        rows = list(query_job.result()) # Chờ kết quả hoàn thành

        sample_data_string = ""
        if rows:
            sample_data_string += f"/*\n{len(rows)} rows from {table_name} table:\n"
            # Lấy tên cột từ kết quả query_job.column_names sẽ chính xác hơn
            # trong trường hợp query có alias hoặc không phải SELECT *
            # Tuy nhiên, với SELECT *, table.schema vẫn ổn.
            column_names = [field.name for field in table.schema]
            sample_data_string += "|".join(column_names) + "\n"
            for row in rows:
                # Truy cập giá trị bằng tên cột từ `row` (là một Row object)
                sample_data_string += "|".join([str(row[col_name]) for col_name in column_names]) + "\n"
            sample_data_string += "*/"
        else:
            sample_data_string = f"/* No sample data found for table {table_name}. */"


        return f"{schema_string}\n\n{sample_data_string}"

    except Exception as e:
        # Trả về thông báo lỗi cụ thể cho bảng này, nhưng không làm dừng toàn bộ quá trình
        error_message = f"-- Error processing table `{table_name}`: {e}\n"
        print(error_message) # In lỗi ra console để debug
        return error_message


def get_table_constraints() -> str:
    fk_pk = """
    ## Ràng buộc khóa chính (Primary Keys)
        | Bảng                           | Cột khóa chính           |
        |--------------------------------|---------------------------|
        | HocVien                        | idHocVien                |
        | HocVien_Lop                   | idHocVien_Lop            |
        | SatHachCNTT_DMKhoaThi         | idKhoaThi                |
        | SatHachCNTT_KhoaThi_Lop       | idLop                    |
        | SatHachCNTT_LichThi           | idLichThi                |
        | SatHachCNTT_PhongThi          | idPhongThi               |
        | SatHachCNTT_KhoaThi_ThiSinh   | idKhoaThi_ThiSinh        |
        | SatHachCNTT_ThiSinh_MonThi    | idThiSinh_MonThi         |
        | SatHachCNTT_DiemThiCB         | idDiemThi                |
        | SatHachCNTT_DiemThiNC         | idDiemThi                |
        | Ref_CapDo                     | idCapDo                  |

    ## Ràng buộc khóa ngoại (Foreign Keys)
        | Bảng                           | Cột khóa ngoại          | Tham chiếu đến (Bảng.Cột)                             |
        |--------------------------------|--------------------------|--------------------------------------------------------|
        | HocVien_Lop                   | idHocVien               | HocVien.idHocVien                                      |
        | HocVien_Lop                   | idLop                   | SatHachCNTT_KhoaThi_Lop.idLop                         |
        | SatHachCNTT_DMKhoaThi         | idCapDo                 | Ref_CapDo.idCapDo                                     |
        | SatHachCNTT_KhoaThi_Lop       | idKhoaThi               | SatHachCNTT_DMKhoaThi.idKhoaThi                       |
        | SatHachCNTT_LichThi           | idKhoaThi               | SatHachCNTT_DMKhoaThi.idKhoaThi                       |
        | SatHachCNTT_PhongThi          | idKhoaThi               | SatHachCNTT_DMKhoaThi.idKhoaThi                       |
        | SatHachCNTT_PhongThi          | idLichThi               | SatHachCNTT_LichThi.idLichThi                         |
        | SatHachCNTT_PhongThi          | idCapDo                 | Ref_CapDo.idCapDo                                     |
        | SatHachCNTT_KhoaThi_ThiSinh   | idKhoaThi               | SatHachCNTT_DMKhoaThi.idKhoaThi                       |
        | SatHachCNTT_KhoaThi_ThiSinh   | idHocVien_Lop           | HocVien_Lop.idHocVien_Lop                             |
        | SatHachCNTT_KhoaThi_ThiSinh   | idCapDo                 | Ref_CapDo.idCapDo                                     |
        | SatHachCNTT_KhoaThi_ThiSinh   | idPhongThi              | SatHachCNTT_PhongThi.idPhongThi                       |
        | SatHachCNTT_ThiSinh_MonThi    | idKhoaThi_ThiSinh       | SatHachCNTT_KhoaThi_ThiSinh.idKhoaThi_ThiSinh         |
        | SatHachCNTT_DiemThiCB         | idKhoaThi_ThiSinh       | SatHachCNTT_KhoaThi_ThiSinh.idKhoaThi_ThiSinh         |
        | SatHachCNTT_DiemThiNC         | idKhoaThi_ThiSinh       | SatHachCNTT_KhoaThi_ThiSinh.idKhoaThi_ThiSinh         |
    """
    return fk_pk

# --- Đây là hàm chính của Tool mới ---
# Hàm này sẽ được gọi bởi AI khi cần thông tin database
# Nó kết hợp lấy schema, mẫu và constraints

# Hàm chính mới
def bigquery_describe_all_tables_tool(client: bigquery.Client, project_id: str, dataset_id: str) -> str:
    # Không cần try...except ở đây nữa vì các hàm con đã xử lý lỗi
    table_names = get_all_table_names(client, project_id, dataset_id)
    if not table_names: # Nếu get_all_table_names trả về rỗng (do lỗi hoặc không có bảng)
        return "Không thể lấy danh sách bảng hoặc không tìm thấy bảng nào trong dataset."

    full_description = ""
    for table_name in table_names:
        # get_table_schema_and_sample giờ đây sẽ trả về thông tin bảng hoặc thông báo lỗi của bảng đó
        table_info = get_table_schema_and_sample(client, project_id, dataset_id, table_name)
        full_description += table_info
        full_description += "\n\n---\n\n" # Phân tách thông tin giữa các bảng

    # Chỉ thêm constraints nếu có ít nhất một bảng được xử lý thành công (hoặc ít nhất là đã thử)
    if full_description: # Kiểm tra xem full_description có nội dung không
        full_description += "\n" + get_table_constraints()
    else: # Trường hợp tất cả các bảng đều lỗi và table_info chỉ trả về thông báo lỗi
        full_description = "Không thể lấy thông tin chi tiết cho bất kỳ bảng nào.\n" + get_table_constraints()


    return full_description

# Import cần thiết cho Tool
from langchain_core.tools import BaseTool

# Tạo class Tool (hoặc dùng decorator @tool tùy version Langchain)
class BigQueryDescribeTablesTool(BaseTool):
    name: str = "BigQueryDescribeTablesTool"
    description: str = description_SQL_hoc_vien
    # Thêm các thuộc tính để truyền client, project_id, dataset_id
    client: bigquery.Client
    project_id: str
    dataset_id: str

    def _run(self) -> str:
        return bigquery_describe_all_tables_tool(self.client, self.project_id, self.dataset_id)

    async def _arun(self) -> str:
         # Triển khai async nếu cần, hoặc raise NotImplementedError
        raise NotImplementedError("Asynchronous execution not supported yet.")
