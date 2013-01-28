{{ package }}import de.zalando.sprocwrapper.SProcCall;
import de.zalando.sprocwrapper.SProcParam;
import de.zalando.sprocwrapper.SProcService;
{{ importList }}
@SProcService(prefix = "{{ prefix }}")
public interface {{ interfaceName }} {
{{ sprocList }}
}
