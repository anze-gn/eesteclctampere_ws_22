import matplotlib.pyplot as plt
import io

# includes a lot of parsing
def plot(data, column):
    plt.plot('recorded_utc', column, '', data=data)
    plt.ylabel(column)
    plt.xticks(rotation=70)
    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight')
    buf.seek(0)
    plt.clf()
    return buf
