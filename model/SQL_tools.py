from google.cloud import bigquery

# Ví dụ hàm lấy thông tin schema và mẫu (có thể dùng lại từ cách LangChain làm hoặc tự viết)
def get_table_schema_and_sample(client: bigquery.Client, project_id: str, dataset_id: str, table_name: str, sample_rows_limit=3):
    try:
        table_ref = client.dataset(dataset_id, project=project_id).table(table_name)
        table = client.get_table(table_ref)

        # Lấy schema (tên cột và kiểu dữ liệu)
        schema_string = f"CREATE TABLE `{table_name}` (\n"
        for field in table.schema:
            schema_string += f"\t`{field.name}` {field.field_type}"
            if field.mode == 'REPEATED':
                 schema_string += ' (REPEATED)' # Kiểu mảng
            elif field.mode == 'NULLABLE':
                 schema_string += ' (NULLABLE)' # Có thể null (thường là mặc định nếu không ghi REQUIRED)
            # Có thể bỏ qua (NULLABLE) nếu muốn schema ngắn gọn
            schema_string += ", \n"
        schema_string = schema_string.rstrip(", \n") + "\n);"

        # Lấy dữ liệu mẫu
        sample_data_string = ""
        query_job = client.query(f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` LIMIT {sample_rows_limit}")
        rows = list(query_job.result())
        if rows:
            sample_data_string += f"/*\n{len(rows)} rows from {table_name} table:\n"
            # Tạo header
            sample_data_string += "\t".join([field.name for field in table.schema]) + "\n"
            # Thêm dữ liệu
            for row in rows:
                sample_data_string += "\t".join([str(row[field.name]) for field in table.schema]) + "\n"
            sample_data_string += "*/"


        return f"{schema_string}\n\n{sample_data_string}"

    except Exception as e:
        return f"Error getting schema/sample for {table_name}: {e}"

def get_table_constraints() -> str:
    fk_pk = """
    ## Ràng buộc khóa chính (Primary Keys)
        | Bảng                        | Cột khóa chính          |
        |----------------------------|--------------------------|
        | HocVien                    | idHocVien                |
        | HocVien_Lop                | idHocVien_lop            |
        | SatHachCNTT_LichThi        | idLichThi                |
        | SatHachCNTT_PhongThi       | idPhongThi               |
        | SatHachCNTT_KhoaThi_ThiSinh| idKhoaThi_ThiSinh        |
        | SatHachCNTT_KhoaThi        | idKhoaThi                |
        | SatHachCNTT_BaiThi         | idBaiThi                 |
        | SatHachCNTT_DeThi          | idDeThi                  |

    ## Ràng buộc khóa ngoại (Foreign Keys)
        | Bảng                        | Cột khóa ngoại          | Tham chiếu đến (Bảng.Cột)       |
        |----------------------------|--------------------------|----------------------------------|
        | HocVien_Lop                | idHocVien                | HocVien.idHocVien                |
        | SatHachCNTT_KhoaThi_ThiSinh| idHocVien                | HocVien.idHocVien                |
        | SatHachCNTT_KhoaThi_ThiSinh| idKhoaThi                | SatHachCNTT_KhoaThi.idKhoaThi    |
        | SatHachCNTT_KhoaThi        | idPhongThi               | SatHachCNTT_PhongThi.idPhongThi  |
        | SatHachCNTT_KhoaThi        | idLichThi                | SatHachCNTT_LichThi.idLichThi    |
        | SatHachCNTT_BaiThi         | idKhoaThi_ThiSinh        | SatHachCNTT_KhoaThi_ThiSinh.idKhoaThi_ThiSinh |
        | SatHachCNTT_BaiThi         | idDeThi                  | SatHachCNTT_DeThi.idDeThi        |
    """
    return fk_pk

# --- Đây là hàm chính của Tool mới ---
# Hàm này sẽ được gọi bởi AI khi cần thông tin database
# Nó kết hợp lấy schema, mẫu và constraints

def bigquery_describe_tables_tool_func(table_names_str: str, client: bigquery.Client, project_id: str, dataset_id: str) -> str:
    """
    Lấy thông tin chi tiết về các bảng BigQuery, bao gồm schema, dữ liệu mẫu và ràng buộc (PK/FK metadata).

    Args:
        table_names_str: Chuỗi chứa tên các bảng cần mô tả, cách nhau bằng dấu phẩy.
                         Ví dụ: "HocVien, SatHachCNTT_DiemThiNC"
        client: Đối tượng BigQuery client đã kết nối.
        project_id: ID của Google Cloud Project.
        dataset_id: ID của Dataset BigQuery.

    Returns:
        Chuỗi mô tả chi tiết các bảng được yêu cầu.
    """
    table_names = [name.strip() for name in table_names_str.split(',') if name.strip()]

    if not table_names:
        # Nếu không có tên bảng được chỉ định, có thể trả về danh sách tất cả các bảng
        # hoặc yêu cầu AI cung cấp tên bảng. Tùy vào thiết kế agent.
        # Tạm thời trả về hướng dẫn
        return "Please provide a comma-separated list of table names to describe."

    full_description = ""

    # Lấy schema và mẫu cho từng bảng
    for table_name in table_names:
        full_description += get_table_schema_and_sample(client, project_id, dataset_id, table_name)
        full_description += "\n\n---\n\n" # Dấu phân cách giữa các bảng

    # Lấy thông tin ràng buộc cho các bảng này
    # (Lưu ý: Hàm get_table_constraints sẽ tự lọc theo tên bảng được truyền vào)
    constraints_info = get_table_constraints()

    full_description += "\n" + constraints_info

    return full_description

# --- Cách tích hợp vào LangChain Toolkit (ví dụ) ---
# Bạn sẽ cần đăng ký hàm bigquery_describe_tables_tool_func này như một Tool trong LangChain.
# Code setup Toolkit của bạn sẽ cần nhận thêm client, project_id, dataset_id
# Ví dụ (dựa trên cấu trúc của bạn):

# Import cần thiết cho Tool
from langchain_core.tools import BaseTool

# Tạo class Tool (hoặc dùng decorator @tool tùy version Langchain)
class BigQueryDescribeTablesTool(BaseTool):
    name: str = "BigQueryDescribeTablesTool"
    description: str = (
        "Input: comma-separated list of table names. "
        "Output: detailed schema, sample data, PRIMARY KEYs, and FOREIGN KEYs metadata for the specified tables. "
        "Use this tool when you need to understand the structure and relationships of specific BigQuery tables before generating complex SQL queries, especially JOINs. "
        "If the user asks about data that likely requires joining multiple tables (like student scores from phone number), call this tool for the relevant tables first (e.g., 'HocVien, HocVien_Lop, SatHachCNTT_KhoaThi_ThiSinh, SatHachCNTT_DiemThiNC, SatHachCNTT_DiemThiCB')."
    )
    # Thêm các thuộc tính để truyền client, project_id, dataset_id
    client: bigquery.Client
    project_id: str
    dataset_id: str

    def _run(self, table_names_str: str) -> str:
        return bigquery_describe_tables_tool_func(table_names_str, self.client, self.project_id, self.dataset_id)

    async def _arun(self, table_names_str: str) -> str:
         # Triển khai async nếu cần, hoặc raise NotImplementedError
        raise NotImplementedError("Asynchronous execution not supported yet.")
