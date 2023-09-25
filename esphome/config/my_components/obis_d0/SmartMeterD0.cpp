#include "esphome/core/log.h"

#include "SmartMeterD0.h"

namespace esphome
{
    namespace obis_d0
    {
        static const char* const TAG = "obis_d0";

        // STX and ETX are sent by an Iskraemeco MT174 after requesting a telegram.
        static constexpr uint8_t STX = 0x02;
        static constexpr uint8_t ETX = 0x02;

        bool SmartMeterD0SensorBase::check_value(const std::string& value)
        {
            bool ok = std::regex_match(value, value_regex_);

            if (!ok)
            {
                ESP_LOGW(TAG, "value regex doesn't match: %s -> %s", obis_code_.c_str(), value.c_str());
            }

            return ok;
        }

        void SmartMeterD0SensorBase::reset_timeout_counter()
        {
            lastUpdate_ = millis();
        }

        bool SmartMeterD0SensorBase::has_timed_out()
        {
            ESP_LOGW(TAG, "Timeout check!");

            auto now = millis();
            if (lastUpdate_ != 0 && now - lastUpdate_ > timeout_)
            {
                lastUpdate_ = 0; // invalidate last update time in case of a timeout
                ESP_LOGE(TAG, "invalidate last update time in case of a timeout");
                return true;
            }
            // no timeout or , ignore reset
            return false;
        }

        SmartMeterD0::SmartMeterD0()
        {
            reset();
        }

        void SmartMeterD0::register_sensor(ISmartMeterD0Sensor* sensor)
        {
            sensors_.emplace(sensor->get_obis_code(), sensor);
        }

        void SmartMeterD0::reset()
        {
            search_ = &SmartMeterD0::search_start_of_telegram;
        }

        void SmartMeterD0::loop()
        {
            while (available() > 0)
            {
                (this->*search_)();
            }

        }

        void SmartMeterD0::search_start_of_telegram()
        {
            uint8_t* dest = &buffer_[length_++];
            (void)read_byte(dest);

            // check if this the start of a telegram
            if (*dest == '/')
            {
                // start of telegram detected
                search_ = &SmartMeterD0::search_end_of_record;
                length_ = 1;
            }
        }

        void SmartMeterD0::search_end_of_record()
        {
            uint8_t* dest = &buffer_[length_++];
            (void)read_byte(dest);

            // check if this the end of a record
            if (*dest == '\n')
            {
                parse_record();
                length_ = 0;
            }
            else if (*dest == STX || *dest == ETX)
            {
                // ignore character
                length_--;
            }

            if (length_ == buffer_.size())
            {
                // abort before overflow
                reset();
                ESP_LOGD(TAG, "abort");
            }
        }

        void SmartMeterD0::parse_record()
        {
            if (length_ < 2)
            {
                // invalid or empty
                ESP_LOGW(TAG, "invalid telegram");
                return;
            }

            if (length_ == 2)
            {
                // empty record
                return;
            }

            if (buffer_[length_ - 2] != '\r')
            {
                // invalid end of record
                ESP_LOGW(TAG, "invalid end or record");
                return;
            }

            switch (buffer_[0])
            {
                case '/':
                    parse_identification();
                    break;

                case '!':
                    end_of_telegram();
                    break;

                default:
                    parse_obis();
                    break;
            }
        }

        void SmartMeterD0::parse_identification()
        {
            std::string ident(reinterpret_cast<const char*>(&buffer_[1]), reinterpret_cast<const char*>(&buffer_[length_ - 2]));

            // search sensor
            auto it = sensors_.find("id");

            if (it != sensors_.end())
            {
                it->second->publish_val(ident);
            }else{
                ESP_LOGW(TAG, "Identification %s not found !", ident.c_str());
            }
        }

        void SmartMeterD0::parse_obis()
        {
            // example: "1-0:0.0.0*255(1023090014472256)\r\n"
            //          |    code     |     value      |

            ESP_LOGD(TAG, "Parse obis data");

            if (length_ < 4)
            {
                ESP_LOGW(TAG, "invalid OBIS length");
                return;
            }

            // check end of OBIS value
            if (buffer_[length_ - 3] != ')')
            {
                ESP_LOGW(TAG, "OBIS value end missing");
                return;
            }

            buffer_[length_ - 3] = 0; // set null terminator at end of OBIS value ")"

            const char* codeStart = reinterpret_cast<const char*>(&buffer_[0]);

            // search begin of OBIS value
            const char* const valueRecordStart = strchr(codeStart, '(');
            if (valueRecordStart == nullptr)
            {
                ESP_LOGW(TAG, "OBIS value start missing");
                return;
            }

            std::string code(reinterpret_cast<const char*>(&buffer_[0]), valueRecordStart);
            std::string value(valueRecordStart + 1, reinterpret_cast<const char*>(&buffer_[length_] - 3));
            const char* const valueStart = valueRecordStart + 1;

            ESP_LOGD(TAG, "OBIS info: %s -> %s", code.c_str(), value.c_str());

            // search sensor
            auto it = sensors_.find(code);

            if (it != sensors_.end())
            {
                it->second->publish_val(value);
            }
        }

        void SmartMeterD0::end_of_telegram()
        {
            for (auto* trigger : telegramTriggers_)
            {
                ESP_LOGD(TAG, "End of telegram found!");
                trigger->trigger();
            }

            reset();
        }

    } // namespace obis_d0
} // namespace esphome