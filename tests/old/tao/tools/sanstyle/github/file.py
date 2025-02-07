def lfs_url(repo, filename, branch='main'):
    '''
    Example
    ===========
    repo: 'SanstyleLab/plotly-datasets'
    branch: 'main'
    filename: 'gapminderDataFiveYear.csv'
    '''
    root = 'https://media.githubusercontent.com/media'
    url = f'{root}/{repo}/{branch}/{filename}'
    return url