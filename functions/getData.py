import pandas as pd
def distancia_curso(distancia_cursos_df:pd.DataFrame, curso_src:int, curso_dst:int) -> int:
    try:
        return distancia_cursos_df.loc[distancia_cursos_df['ID CURSO'] == curso_dst][[str(curso_src)]].values[0][0]
    except:
        return False