import sys 
import pathlib as pl
asterstudy_path = pl.Path(__file__).parent.parent.absolute()  
sys.path.append(str(asterstudy_path))
code_aster_path = asterstudy_path / "asterstudy" / "code_aster_version"
sys.path.append(str(code_aster_path))

