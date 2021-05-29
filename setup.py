import os, sys, subprocess


def buildProgramConfig(
        descriptive_name='Supervised Program',
        program_name=None,
        command=None,
        project_dir=None,
        user=None,
        num_procs='1',
        out_logfile=None,
        err_logfile=None,
        autostart=False,
        autorestart=True,
        startsecs=10,
        stopwaitsecs=600,
        killasgroup=True,
        priority=9999):

    with open('supervisor/supervisor-program-template.ini', 'r') as file:
        config_str = file.read()

    config_str = config_str.replace('{DESCRIPTIVE_NAME}', descriptive_name)

    if not program_name:
        print("ERRO: Nome do programa faltando.")
        return None
    else:
        config_str = config_str.replace('{PROGRAM_NAME}', program_name)

    if not command:
        print("ERRO: Caminho do comando faltando.")
        return None
    else:
        config_str = config_str.replace('{COMMAND}', command)

    if not project_dir:
        print("ERRO: Diretorio do projeto faltando.")
        return None
    else:
        config_str = config_str.replace('{PROJECT_DIR}', project_dir)

    if not user:
        print("ERRO: Nome do usuário dono do processo faltando.")
        return None
    else:
        config_str = config_str.replace('{USER}', user)

    config_str = config_str.replace('{NUM_PROCS}', str(num_procs))

    if not out_logfile:
        print("ERRO: Caminho do arquivo de stdout log faltando.")
        return None
    else:
        config_str = config_str.replace('{OUT_LOG_FILE}', out_logfile)
        with open(out_logfile, 'w') as file:
            file.write('')

    if not err_logfile:
        print("ERRO: Caminho do arquivo de stderr faltando.")
        return None
    else:
        config_str = config_str.replace('{ERR_LOG_FILE}', err_logfile)
        with open(err_logfile, 'w') as file:
            file.write('')

    config_str = config_str.replace('{AUTOSTART}', str(autostart).lower())

    config_str = config_str.replace('{AUTORESTART}', str(autorestart).lower())

    config_str = config_str.replace('{STARTSECS}', str(startsecs))

    config_str = config_str.replace('{STOPWAITSECS}', str(stopwaitsecs))

    config_str = config_str.replace('{KILLASGROUP}', str(killasgroup).lower())

    config_str = config_str.replace('{PRIORITY}', str(priority))

    return config_str


#TODO: Esse script todo é um rascunho. Usar a lib click pra melhora-lo depois.
if __name__=='__main__':

    # Verifica se supervisor está presente.
    try:
        subprocess.call(['supervisorctl', '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        print('ERRO: Instale o supervisor primeiro.')
        exit()

    # Vamos escrever coisas em /etc, o que só pode ser feito como usuário raiz.
    if os.geteuid() != 0:
        print('ERRO: É necessário executar com sudo.')
        exit()

    # Pra eu não esquecer dessa parada.
    if len(sys.argv) < 3:
        print('Uso:\n sudo python setup.py username /abs/path/to/supervisor.d/confs/dir')
        exit()

    # Coisas que não tem como não serem argumentos.
    user = sys.argv[1]
    supervisor_d_dir = sys.argv[2]

    # Determina diretório do projeto.
    project_location = os.path.dirname(os.path.abspath(__file__))

    # Determina diretório dos logs.
    output_dir = os.path.join(project_location, 'logs')

    # Certifica a existência do diretório dos logs.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif not os.path.isdir(output_dir):
        print(f'ERRO: {output_dir} não é um diretório.')

    # Celery Pure - Worker
    config_str_worker = buildProgramConfig('Djangelery - Worker',
                                    'djangelery-worker',
                                    os.path.join(project_location, 'celery_worker.sh'),
                                    project_location,
                                    user,
                                    1,
                                    os.path.join(output_dir, 'djangelery-worker.log'),
                                    os.path.join(output_dir, 'djangelery-worker.log'),
                                    autostart=False,
                                    priority=998)

    # Celery Pure - Beat
    config_str_beat = buildProgramConfig('Djangelery - Beat',
                                    'djangelery-beat',
                                    os.path.join(project_location, 'celery_beat.sh'),
                                    project_location,
                                    user,
                                    1,
                                    os.path.join(output_dir, 'djangelery-beat.log'),
                                    os.path.join(output_dir, 'djangelery-beat.log'),
                                    autostart=False,
                                    priority=999)

    # Escreve configuração do worker.
    filepath = os.path.join(supervisor_d_dir, 'djangelery-worker.ini')
    with open(filepath, 'w') as file:
        file.write(config_str_worker)

    # Escreve configuração do beat.
    filepath = os.path.join(supervisor_d_dir, 'djangelery-beat.ini')
    with open(filepath, 'w') as file:
        file.write(config_str_beat)

    subprocess.call(['chown', '-R', user, output_dir])
    subprocess.call(['chgrp', '-R', user, output_dir])

    print('Done.')
