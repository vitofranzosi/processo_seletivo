// Caixa de correio local: recebe o e-mail do código de acesso e devolve os seis dígitos.
import net from 'node:net';

export function caixaDeCorreio(porta = 1035) {
  const recebidas = [];
  const servidor = net.createServer(sock => {
    let dados = '', emDados = false;
    sock.write('220 localhost SMTP\r\n');
    sock.on('data', buf => {
      for (const linha of buf.toString().split(/\r?\n/)) {
        if (emDados) {
          if (linha === '.') { emDados = false; recebidas.push(dados); dados = ''; sock.write('250 OK\r\n'); }
          else dados += linha + '\n';
          continue;
        }
        const c = linha.trim().toUpperCase();
        if (!c) continue;
        if (c.startsWith('EHLO') || c.startsWith('HELO')) sock.write('250 localhost\r\n');
        else if (c.startsWith('MAIL') || c.startsWith('RCPT')) sock.write('250 OK\r\n');
        else if (c.startsWith('DATA')) { emDados = true; sock.write('354 End with .\r\n'); }
        else if (c.startsWith('QUIT')) { sock.write('221 Bye\r\n'); sock.end(); }
        else if (c.startsWith('RSET') || c.startsWith('NOOP')) sock.write('250 OK\r\n');
        else sock.write('250 OK\r\n');
      }
    });
    sock.on('error', () => {});
  });
  servidor.listen(porta);
  return {
    async codigo(timeoutMs = 15000) {
      const ate = Date.now() + timeoutMs;
      while (Date.now() < ate) {
        for (let i = recebidas.length - 1; i >= 0; i--) {
          const m = recebidas[i].match(/\b(\d{6})\b/);
          if (m) { recebidas.length = 0; return m[1]; }
        }
        await new Promise(r => setTimeout(r, 250));
      }
      throw new Error('nenhum código chegou');
    },
    fechar() { servidor.close(); },
  };
}
