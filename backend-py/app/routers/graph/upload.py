from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from app.services.graph.dealtxt import convert_to_jsonl_with_prefix
from app.services.graph.dealcsv import convert_csv_to_jsonl_with_prefix
from app.services.graph.dealxlsx import convert_xlsx_to_jsonl_with_prefix
from app.services.graph.dealdocx import convert_docx_to_jsonl_with_prefix

router = APIRouter()

@router.post("/graph/upload")
async def upload_graph_file(
    Topic: str = Form(...),
    file: UploadFile = File(...),
    user_id: int = Form(...),
    is_admin: bool = Form(False)
):
    """
    上传图数据文件并导入到Neo4j数据库
    
    参数:
    - Topic: 主题名称
    - file: 上传的文件（支持txt、csv、xlsx、docx格式）
    - user_id: 用户ID，用于权限控制
    - is_admin: 是否为管理员，默认为False。管理员上传的数据user_id为0（公共节点）
    
    返回:
    - success: 是否成功
    - output_jsonl: 生成的JSONL文件路径
    - output_txt: 生成的TXT文件路径
    - output_csv: 生成的CSV文件路径
    - csv_data: CSV数据内容
    """
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads/graphData'))
    os.makedirs(temp_dir, exist_ok=True)
    # 文件名加上Topic和唯一编码，避免冲突
    import uuid
    unique_code = uuid.uuid4().hex[:8]
    base_name, ext_name = os.path.splitext(file.filename)
    file_path = os.path.join(temp_dir, f"{Topic}_{unique_code}_{base_name}{ext_name}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 判断文件类型
    ext = file.filename.split('.')[-1].lower()
    output_jsonl = os.path.join(temp_dir, f"{Topic}_{unique_code}_output.jsonl")
    output_txt = os.path.join(temp_dir, f"{Topic}_{unique_code}_output.txt")
    prefix = f"$${Topic}$$"
    import logging
    logger = logging.getLogger("uvicorn.error")
    try:
        logger.info(f"收到上传请求: Topic={Topic}, file={file.filename}, ext={ext}")
        if ext == "txt":
            logger.info("处理txt文件...")
            from app.services.graph.dealtxt import convert_to_jsonl_with_prefix, extract_text_to_jsonl
            convert_to_jsonl_with_prefix(file_path, output_jsonl, prefix)
            logger.info(f"已生成JSONL: {output_jsonl}")
            extract_text_to_jsonl(output_jsonl, output_txt)
            logger.info(f"已生成TXT: {output_txt}")
        elif ext == "csv":
            logger.info("处理csv文件...")
            from app.services.graph.dealcsv import process_csv_to_txt
            process_csv_to_txt(file_path, output_jsonl, output_txt, prefix)
            logger.info(f"已生成JSONL: {output_jsonl}, TXT: {output_txt}")
        elif ext == "xlsx":
            logger.info("处理xlsx文件...")
            from app.services.graph.dealxlsx import process_xlsx_to_txt
            process_xlsx_to_txt(file_path, output_jsonl, output_txt, prefix)
            logger.info(f"已生成JSONL: {output_jsonl}, TXT: {output_txt}")
        elif ext == "docx":
            logger.info("处理docx文件...")
            from app.services.graph.dealdocx import process_docx_to_txt
            process_docx_to_txt(file_path, output_jsonl, output_txt, prefix)
            logger.info(f"已生成JSONL: {output_jsonl}, TXT: {output_txt}")
        else:
            logger.error(f"不支持的文件类型: {ext}")
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        # 处理完txt后，默认使用Qwen抽取；下面保留旧predict_uie代码作为历史回退参考。
        csv_output = os.path.join(temp_dir, f"{Topic}_{unique_code}_output.csv")
        logger.info(f"调用 Qwen 抽取图谱字段: txt={output_txt}, csv={csv_output}")
        from app.services.graph.qwen_extractor import extract_graph_csv_with_qwen
        await extract_graph_csv_with_qwen(Topic, output_txt, csv_output)
        logger.info(f"已生成CSV: {csv_output}")

        from app.services.graph.import_to_neo4j import import_csv_to_neo4j
        logger.info(f"导入到Neo4j: {csv_output}, user_id={user_id}, is_admin={is_admin}")
        actual_user_id = 0 if is_admin else user_id
        import_csv_to_neo4j(csv_output, actual_user_id)
        logger.info("Neo4j导入完成")

        import csv as pycsv
        csv_data = []
        with open(csv_output, 'r', encoding='utf-8') as f:
            reader = pycsv.DictReader(f)
            for row in reader:
                csv_data.append(row)
        logger.info(f"返回csv数据，条数: {len(csv_data)}")

        return JSONResponse({
            "success": True,
            "output_jsonl": output_jsonl,
            "output_txt": output_txt,
            "output_csv": csv_output,
            "csv_data": csv_data
        })
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services/graph/ie_ckpts'))
        logger.info(f"调用predict_uie: txt={output_txt}, csv={csv_output}")
        try:
            from app.services.graph.predict_uie import predict_uie
            predict_uie(
                model_name_or_path=model_path,
                data_file=output_txt,
                output_file=csv_output
            )
            logger.info(f"已生成CSV: {csv_output}")
        except ModuleNotFoundError as e:
            if 'paddle' in str(e):
                logger.warning("paddle未安装，自动切换到potatopytorch环境执行predict_uie.py")
                import subprocess
                from dotenv import load_dotenv
                
                # 加载环境变量
                load_dotenv()
                
                potatopy_env_python = os.getenv('PYTHON_INTERPRETER_PATH', r"D:\Anaconda3\envs\potatopytorch\python.exe")  # 请根据实际路径修改
                script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services/graph/predict_uie.py'))
                cmd = [potatopy_env_python, script_path,
                       '--model_name_or_path', model_path,
                       '--data_file', output_txt,
                       '--output_file', csv_output]
                logger.info(f"subprocess调用: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                logger.info(f"subprocess stdout: {result.stdout}")
                if result.returncode != 0:
                    logger.error(f"subprocess执行失败: {result.stderr}")
                    raise HTTPException(status_code=500, detail=f"paddle环境推理失败: {result.stderr}")
                logger.info(f"已生成CSV: {csv_output}")
            else:
                logger.error(f"ModuleNotFoundError: {str(e)}")
                raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
        # 导入到Neo4j
        from app.services.graph.import_to_neo4j import import_csv_to_neo4j
        logger.info(f"导入到Neo4j: {csv_output}, user_id={user_id}, is_admin={is_admin}")
        # 确定实际的user_id：管理员为0，普通用户使用传入的user_id
        actual_user_id = 0 if is_admin else user_id
        import_csv_to_neo4j(csv_output, actual_user_id)
        logger.info("Neo4j导入完成")
        # 读取csv内容并转为json返回
        import csv as pycsv
        csv_data = []
        with open(csv_output, 'r', encoding='utf-8') as f:
            reader = pycsv.DictReader(f)
            for row in reader:
                csv_data.append(row)
        logger.info(f"返回csv数据，条数: {len(csv_data)}")
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

    return JSONResponse({
        "success": True,
        "output_jsonl": output_jsonl,
        "output_txt": output_txt,
        "output_csv": csv_output,
        "csv_data": csv_data
    })
