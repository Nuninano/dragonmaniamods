import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;

/**
 * Herramienta de firma para el manifiesto de actualizaciones (solo necesitas Java 11+, sin dependencias).
 *   java SignTool.java gen                  -> crea mods_signing.key (PRIVADA, guardala) y muestra la clave publica (hex)
 *   java SignTool.java sign updates.json    -> crea updates.json.sig (subelo junto a updates.json)
 * La clave publica (hex) va en updates.cfg del juego:  pubkey=<hex>   (y allow_code=1 solo si quieres mods con codigo)
 */
public class SignTool {
    static String hex(byte[] b) { StringBuilder s = new StringBuilder(); for (byte x : b) s.append(String.format("%02x", x & 0xff)); return s.toString(); }
    static byte[] unhex(String s) { byte[] b = new byte[s.length() / 2]; for (int i = 0; i < b.length; i++) b[i] = (byte) Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16); return b; }

    public static void main(String[] a) throws Exception {
        if (a.length >= 1 && a[0].equals("gen")) {
            Path k = Paths.get("mods_signing.key");
            if (Files.exists(k)) { System.out.println("Ya existe mods_signing.key: no se sobrescribe."); return; }
            KeyPairGenerator g = KeyPairGenerator.getInstance("RSA");
            g.initialize(3072);
            KeyPair kp = g.generateKeyPair();
            Files.write(k, hex(kp.getPrivate().getEncoded()).getBytes("UTF-8"));
            System.out.println("Clave PRIVADA guardada en mods_signing.key (NO la compartas ni la subas a GitHub).");
            System.out.println("Clave PUBLICA (pegala en updates.cfg como pubkey=):");
            System.out.println(hex(kp.getPublic().getEncoded()));
        } else if (a.length >= 2 && a[0].equals("sign")) {
            byte[] priv = unhex(new String(Files.readAllBytes(Paths.get("mods_signing.key")), "UTF-8").trim());
            PrivateKey pk = KeyFactory.getInstance("RSA").generatePrivate(new PKCS8EncodedKeySpec(priv));
            Signature s = Signature.getInstance("SHA256withRSA");
            s.initSign(pk);
            s.update(Files.readAllBytes(Paths.get(a[1])));
            Files.write(Paths.get(a[1] + ".sig"), hex(s.sign()).getBytes("UTF-8"));
            System.out.println("Firma escrita en " + a[1] + ".sig");
        } else {
            System.out.println("Uso:\n  java SignTool.java gen\n  java SignTool.java sign updates.json");
        }
    }
}
