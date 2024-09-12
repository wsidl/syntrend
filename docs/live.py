from livereload import Server, shell
import pathlib

CMD = 'uv run poe docs'

if __name__ == '__main__':
    server = Server()
    server.watch('**/*.rst', shell(CMD), delay=1)
    server.watch('docs/**/*.md', shell(CMD), delay=1)
    server.watch('docs/**/*.py', shell(CMD), delay=1)
    server.watch('docs/_static/*', shell(CMD), delay=1)
    server.watch('docs/_templates/*', shell(CMD), delay=1)
    server.serve(root='dist')
